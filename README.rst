.. code-block:: python

    from deploy5k.api import (reserve,
                              deploy,
                              configure_network)
    import json
    import logging
    logging.basicConfig(level=logging.DEBUG)

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
            "secondary_networks": ["network2", "network3"]
        }],
        "networks": [{"type": "prod", "role": "network1", "site": "nancy"},
            {"type": "kavlan", "role": "network2", "site": "nancy"},
            {"type": "kavlan-global", "role": "network3", "site": "lille"}]
    }

    # Follow this workflow :
    #
    # It's idempotent and stateless
    #
    # resources will be decorated with some extra information : the _c_* keys
    c_resources = reserve(resources, job_name="test", walltime="01:00:00")
    c_resources = deploy(c_resources)
    c_resources = configure_network(c_resources)

    # And you'll end up with : 
    print(json.dumps(c_resources, indent=4))
    """
    {
        "networks": [
            {
                "role": "network1",
                "type": "prod",
                "site": "nancy",
                "_c_network": {
                    "site": "nancy",
                    "gateway": "172.16.79.254",
                    "vlan_id": null,
                    "network": "172.16.64.0/20"
                }
            },
            {
                "role": "network2",
                "type": "kavlan",
                "site": "nancy",
                "_c_network": {
                    "site": "nancy",
                    "gateway": "10.16.63.254",
                    "vlan_id": 4,
                    "network": "10.16.0.0/18"
                }
            },
            {
                "role": "network3",
                "type": "kavlan-global",
                "site": "lille",
                "_c_network": {
                    "site": "lille",
                    "gateway": "10.11.255.254",
                    "vlan_id": 12,
                    "network": "10.11.192.0/18"
                }
            }
        ],
        "machines": [
            {
                "_c_nics": [
                    [
                        "eth0",
                        "network1"
                    ],
                    [
                        "eth1",
                        "network2"
                    ],
                    [
                        "eth2",
                        "network3"
                    ]
                ],
                "primary_network": "network1",
                "_c_deployed": [
                    "grisou-40.nancy.grid5000.fr"
                ],
                "cluster": "grisou",
                "role": "compute",
                "_c_nodes": [
                    "grisou-40.nancy.grid5000.fr"
                ],
                "nodes": 1,
                "_c_undeployed": [],
                "secondary_networks": [
                    "network2",
                    "network3"
                ]
            },
            {
                "_c_nics": [
                    [
                        "eth0",
                        "network1"
                    ],
                    [
                        "eth1",
                        "network2"
                    ],
                    [
                        "eth2",
                        "network3"
                    ]
                ],
                "primary_network": "network1",
                "_c_deployed": [
                    "grisou-43.nancy.grid5000.fr"
                ],
                "cluster": "grisou",
                "role": "control",
                "_c_nodes": [
                    "grisou-43.nancy.grid5000.fr"
                ],
                "nodes": 1,
                "_c_undeployed": [],
                "secondary_networks": [
                    "network2",
                    "network3"
                ]
            }
        ]
    }
    """
