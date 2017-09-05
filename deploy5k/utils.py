import copy
import execo_g5k as ex5
import execo_g5k.api_utils as api
import logging
from deploy5k.error import MissingNetworkError
from execo import Host
from itertools import groupby
from schema import PROD, KAVLAN_GLOBAL, KAVLAN_LOCAL, KAVLAN


def is_prod(net):
    return net["type"] == PROD


def to_vlan_type(vlan_id):
    if vlan_id < 4:
        return KAVLAN_LOCAL
    elif vlan_id < 10:
        return KAVLAN
    return KAVLAN_GLOBAL


def get_or_create_job(resources, job_name, walltime):
    gridjob, _ = ex5.planning.get_job_by_name(job_name)
    if gridjob is None:
        gridjob = make_reservation(resources, job_name, walltime)
    logging.info("Waiting for oargridjob %s to start" % gridjob)
    ex5.wait_oargrid_job_start(gridjob)
    return gridjob


def concretize_resources(resources, gridjob):
    nodes = ex5.get_oargrid_job_nodes(gridjob)
    c_resources = concretize_nodes(resources, nodes)

    job_sites = ex5.get_oargrid_job_oar_jobs(gridjob)
    vlans = []
    for (job_id, site) in job_sites:
        vlan_ids = ex5.get_oar_job_kavlan(job_id, site)
        vlans.extend([{
            "site": site,
            "vlan_id": vlan_id} for vlan_id in vlan_ids])

    c_resources = concretize_networks(c_resources, vlans)
    return c_resources


def _deploy(nodes, force_deploy, options):
    # For testing purpose
    logging.info("Deploying %s with options %s" % (nodes, options))
    dep = ex5.Deployment(nodes, **options)
    return ex5.deploy(dep, check_deployed_command=not force_deploy)


def mount_nics(c_resources):
    machines = c_resources["machines"]
    networks = c_resources["networks"]
    for desc in machines:
        primary_nic = get_cluster_interfaces(desc["cluster"],
                                             lambda nic: nic['mounted'])[0]
        desc["_c_nics"] = [(primary_nic, desc["primary_network"])]
        _mount_secondary_nics(desc, networks)
    return c_resources


def _mount_secondary_nics(desc, networks):
    cluster = desc["cluster"]
    site = ex5.get_cluster_site(cluster)
    # get only the secondary interfaces
    nics = get_cluster_interfaces(cluster, lambda nic: not nic['mounted'])
    idx = 0
    desc["_c_nics"] = desc.get("_c_nics") or []
    for network_role in desc["secondary_networks"]:
        net = lookup_networks(network_role, networks)
        if net["type"] == PROD:
            # nothing to do
            continue
        nic = nics[idx]
        nodes_to_set = [Host(n) for n in desc["_c_nodes"]]
        vlan_id = net["_c_network"]["vlan_id"]
        logging.info("Put %s in vlan id %s for nodes %s" % (nic,
                                                            vlan_id,
                                                            nodes_to_set))
        api.set_nodes_vlan(site,
                           nodes_to_set,
                           nic,
                           vlan_id)
        # recording the mapping, just in case
        desc["_c_nics"].append((nic, network_role))
        idx = idx + 1


def get_cluster_interfaces(cluster, extra_cond=lambda nic: True):
    site = ex5.get_cluster_site(cluster)
    nics = ex5.get_resource_attributes(
        "/sites/%s/clusters/%s/nodes" % (site, cluster))
    nics = nics['items'][0]['network_adapters']
    nics = [nic['device'] for nic in nics
           if nic['mountable'] and
           nic['interface'] == 'Ethernet' and
           not nic['management'] and extra_cond(nic)]
    nics = sorted(nics)
    return nics


def lookup_networks(network_role, networks):
    match = [net for net in networks if net["role"] == network_role]
    # if it has been validated the following is valid
    return match[0]


def mk_pools(things, keyfnc=lambda x: x):
    "Indexes a thing by the keyfnc to construct pools of things."
    pools = {}
    sthings = sorted(things, key=keyfnc)
    for key, thingz in groupby(sthings, key=keyfnc):
        pools.setdefault(key, []).extend(list(thingz))
    return pools


def pick_things(pools, key,  n):
    "Picks a maximum of n things in a dict of indexed pool of things."
    pool = pools.get(key)
    if not pool:
        return []
    things = pool[:n]
    del pool[:n]
    return things


def concretize_nodes(resources, nodes):
    # force order to be a *function*
    snodes = sorted(nodes, key=lambda n: n.address)
    pools = mk_pools(snodes, lambda n: n.address.split('-')[0])
    machines = resources["machines"]
    for desc in machines:
        cluster = desc["cluster"]
        nb = desc["nodes"]
        c_nodes = pick_things(pools, cluster, nb)
        #  put concrete hostnames here
        desc["_c_nodes"] = [c_node.address for c_node in c_nodes]
    return resources


def concretize_networks(resources, vlans):
    c_resources = copy.deepcopy(resources)
    s_vlans = sorted(vlans, key=lambda v: (v["site"], v["vlan_id"]))
    pools = mk_pools(s_vlans,
                     lambda n: (n["site"], to_vlan_type(n["vlan_id"])))
    for desc in c_resources["networks"]:
        site = desc["site"]
        site_info = ex5.get_resource_attributes('/sites/%s' % site)
        n_type = desc["type"]
        if n_type == PROD:
            desc["_c_network"] = {"site": site, "vlan_id": None}
            desc["_c_network"].update(site_info["kavlans"]["default"])
        else:
            networks = pick_things(pools, (site, n_type), 1)
            if len(networks) < 1:
                raise MissingNetworkError(site, n_type)
            # concretize the network
            desc["_c_network"] = networks[0]
            vlan_id = desc["_c_network"]["vlan_id"]
            desc["_c_network"].update(site_info["kavlans"][str(vlan_id)])

    return c_resources


def make_reservation(resources, job_name, walltime):
    machines = resources["machines"]
    networks = resources["networks"]

    criteria = {}
    # machines reservations
    for desc in machines:
        cluster = desc["cluster"]
        nodes = desc["nodes"]
        site = api.get_cluster_site(cluster)
        criterion = "{cluster='%s'}/nodes=%s" % (cluster, nodes)
        criteria.setdefault(site, []).append(criterion)

    # network reservations
    non_prod = [network for network in networks if network["type"] != "prod"]
    for desc in non_prod:
        site = desc["site"]
        n_type = desc["type"]
        criterion = "{type='%s'}/vlan=1" % n_type
        criteria.setdefault(site, []).append(criterion)

    jobs_specs = [(ex5.OarSubmission(resources='+'.join(c),
                                 name=job_name), s)
                    for s, c in criteria.items()]

    # Make the reservation
    gridjob, _ = ex5.oargridsub(
        jobs_specs,
        walltime=walltime.encode('ascii', 'ignore'),
        job_type='deploy')

    if gridjob is None:
        raise Exception('No oar job was created')
    return gridjob
