from itertools import groupby
from operator import itemgetter, add
import deploy5k.utils as utils
import schema
import copy

ENV_NAME = "jessie-x64-min"
JOB_NAME = "deploy5k"
WALLTIME = "02:00:00"


def reserve(resources,
            job_name=JOB_NAME,
            walltime=WALLTIME):
    schema.validate_schema(resources)
    gridjob = utils.get_or_create_job(resources, job_name, walltime)
    c_resources = copy.deepcopy(resources)
    c_resources = utils.concretize_resources(c_resources, gridjob)
    return c_resources


def deploy(c_resources, env_name=ENV_NAME, force_deploy=False):
    c_resources = copy.deepcopy(c_resources)
    machines = c_resources["machines"]
    networks = c_resources["networks"]
    key = itemgetter("primary_network")
    s_machines = sorted(machines, key=key)
    for primary_network, i_descs in groupby(s_machines, key=key):
        descs = list(i_descs)
        nodes = [desc["_c_nodes"] for desc in descs]
        nodes = reduce(add, nodes)
        net = utils.lookup_networks(primary_network, networks)
        options = {
            "env_name": env_name
        }
        if not utils.is_prod(net):
            options.update({"vlan": net["_c_network"]["vlan_id"]})
        # Yes, this is sequential
        deployed, undeployed = utils._deploy(nodes, force_deploy, options)
        for desc in descs:
            desc["_c_deployed"] = list(set(desc["_c_nodes"]) & set(deployed))
            desc["_c_undeployed"] = list(set(desc["_c_nodes"]) &
                                         set(undeployed))

    return c_resources


def configure_network(c_resources, dhcp=False):
    c_resources = copy.deepcopy(c_resources)
    c_resources = utils.mount_nics(c_resources)
    # TODO(msimonin): run dhcp if asked
    return c_resources
