import copy
import execo_g5k as ex5
import execo_g5k.api_utils as api
from itertools import groupby
from schema import validate_schema, PROD, KAVLAN_GLOBAL, KAVLAN_LOCAL, KAVLAN
from deploy5k.error import MissingNetworkError


def to_vlan_type(vlan_id):
    if vlan_id < 4:
        return KAVLAN_LOCAL
    elif vlan_id < 10:
        return KAVLAN
    return KAVLAN_GLOBAL


def get_or_create_job(jobname, resources):
    validate_schema(resources)
    gridjob, _ = ex5.planning.get_job_by_name(jobname)
    if gridjob is None:
        gridjob = make_reservation(resources)
    ex5.wait_oargrid_job_start(gridjob)
    return gridjob


def concretize_resources(gridjob, resources):
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


def mk_pools(things, keyfnc=lambda x: x):
    "Indexes a thing by the keyfnc to construct pools of things."
    pools = {}
    sthings = sorted(things, key=keyfnc)
    for key, thingz in groupby(sthings, key=keyfnc):
        pools.setdefault(key, []).extend(list(thingz))
    return pools


def pick_things(pools, key,  n):
    "Picks a maximum of n things in a pool of indexed things."
    pool = pools.get(key)
    if not pool:
        return []
    things = pool[:n]
    del pool[:n]
    return things


def concretize_nodes(resources, nodes):
    c_resources = copy.deepcopy(resources)
    # force order to be a *function*
    snodes = sorted(nodes, key=lambda n: n.address)
    pools = mk_pools(snodes, lambda n: n.address.split('-')[0])
    machines = c_resources["machines"]
    for desc in machines:
        cluster = desc["cluster"]
        nb = desc["nodes"]
        c_nodes = pick_things(pools, cluster, nb)
        desc["_c_nodes"] = c_nodes
    return c_resources


def concretize_networks(resources, vlans):
    c_resources = copy.deepcopy(resources)
    s_vlans = sorted(vlans, key=lambda v: (v["site"], v["vlan_id"]))
    no_prod = [n for n in c_resources["networks"] if n["type"] != PROD]
    pools = mk_pools(s_vlans,
                     lambda n: (n["site"], to_vlan_type(n["vlan_id"])))
    for desc in no_prod:
        site = desc["site"]
        n_type = desc["type"]
        networks = pick_things(pools, (site, n_type), 1)
        if len(networks) < 1:
            raise MissingNetworkError(site, n_type)
        desc["_c_vlan_id"] = networks[0]
    return c_resources


def make_reservation(resources):
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
                                 name="test"), s)
                    for s, c in criteria.items()]

    # Make the reservation
    gridjob, _ = ex5.oargridsub(
        jobs_specs,
        walltime="02:00:00".encode('ascii', 'ignore'),
        job_type='deploy')

    if gridjob is None:
        raise Exception('No oar job was created')
    return gridjob
