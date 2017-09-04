* Util functions to deploy nodes and network on Grid'5000


```
from deploy5k.deploy import get_or_create_job, concretize_resources

resources = {
    "machines": [{
        "role": "compute",
        "nodes": 1,
        "cluster": "grisou",
        "primary_network": "network1",
        "secondary_networks": ["network2", "network3"]
    }, {
        "role": "control",
        "nodes": 1,
        "cluster": "grisou",
        "primary_network": "network1",
        "secondary_networks": ["network2"]
    }],
    "networks": [{"type": "prod", "role": "network1", "site": "nancy"},
        {"type": "kavlan", "role": "network2", "site": "nancy"},
        {"type": "kavlan-global", "role": "network3", "site": "lille"}]
}

gridjob = get_or_create_job("test", resources)
res = concretize_resources(gridjob, resources)

# res
{'networks': [{'role': 'network1', 'type': 'prod', 'site': 'nancy'}, {'_c_vlan_id': {'site': 'nancy', 'vlan_id': 4}, 'role': 'network2', 'type': 'kavlan', 'site': 'nancy'}, {'_c_vlan_id': {'site': 'lille', 'vlan_id': 12}, 'role': 'network3', 'type': 'kavlan-global', 'site': 'lille'}], 'machines': [{'primary_network': 'network1', 'cluster': 'grisou', 'role': 'compute', '_c_nodes': [Host('grisou-33.nancy.grid5000.fr')], 'nodes': 1, 'secondary_networks': ['network2', 'network3']}, {'primary_network': 'network1', 'cluster': 'grisou', 'role': 'control', '_c_nodes': [Host('grisou-34.nancy.grid5000.fr')], 'nodes': 1, 'secondary_networks': ['network2', 'network3']}]}
```
