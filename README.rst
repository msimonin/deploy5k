.. code-block:: python

    from deploy5k.deploy import (get_or_create_job, 
                                 concretize_resources,
                                 deploy,
                                 mount_nics)
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

    gridjob = get_or_create_job("test", resources)
    c_resources = concretize_resources(gridjob, resources)
    print(json.dumps(c_resources, indent=4))
    """
    res=
    {
        "networks": [
            {
                "role": "network1",
                "type": "prod",
                "site": "nancy",
                "_c_network": {
                    "network": "172.16.64.0/20",
                    "site": "nancy",
                    "vlan_id": null,
                    "gateway": "172.16.79.254"
                }
            },
            {
                "role": "network2",
                "type": "kavlan",
                "site": "nancy",
                "_c_network": {
                    "network": "10.16.128.0/18",
                    "site": "nancy",
                    "vlan_id": 6,
                    "gateway": "10.16.191.254"
                }
            },
            {
                "role": "network3",
                "type": "kavlan-global",
                "site": "lille",
                "_c_network": {
                    "network": "10.11.192.0/18",
                    "site": "lille",
                    "vlan_id": 12,
                    "gateway": "10.11.255.254"
                }
            }
        ],
        "machines": [
            {
                "primary_network": "network1",
                "cluster": "grisou",
                "role": "compute",
                "_c_nodes": [
                    "grisou-46.nancy.grid5000.fr"
                ],
                "nodes": 1,
                "secondary_networks": [
                    "network2",
                    "network3"
                ]
            },
            {
                "primary_network": "network1",
                "cluster": "grisou",
                "role": "control",
                "_c_nodes": [
                    "grisou-49.nancy.grid5000.fr"
                ],
                "nodes": 1,
                "secondary_networks": [
                    "network2",
                    "network3"
                ]
            }
        ]
    }
    """

    c_resources = deploy(c_resources)
    print(json.dumps(c_resources, indent=4))

    """
    {
        "networks": [
            {
                "type": "prod",
                "role": "network1",
                "site": "nancy",
                "_c_network": {
                    "gateway": "172.16.79.254",
                    "network": "172.16.64.0/20",
                    "vlan_id": null,
                    "site": "nancy"
                }
            },
            {
                "type": "kavlan",
                "role": "network2",
                "site": "nancy",
                "_c_network": {
                    "gateway": "10.16.191.254",
                    "network": "10.16.128.0/18",
                    "vlan_id": 6,
                    "site": "nancy"
                }
            },
            {
                "type": "kavlan-global",
                "role": "network3",
                "site": "lille",
                "_c_network": {
                    "gateway": "10.11.255.254",
                    "network": "10.11.192.0/18",
                    "vlan_id": 12,
                    "site": "lille"
                }
            }
        ],
        "machines": [
            {
                "primary_network": "network1",
                "_c_deployed": [
                    "grisou-46.nancy.grid5000.fr"
                ],
                "cluster": "grisou",
                "role": "compute",
                "_c_nodes": [
                    "grisou-46.nancy.grid5000.fr"
                ],
                "nodes": 1,
                "_c_undeployed": [],
                "secondary_networks": [
                    "network2",
                    "network3"
                ]
            },
            {
                "primary_network": "network1",
                "_c_deployed": [
                    "grisou-49.nancy.grid5000.fr"
                ],
                "cluster": "grisou",
                "role": "control",
                "_c_nodes": [
                    "grisou-49.nancy.grid5000.fr"
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

    c_resources = mount_nics(c_resources)
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
                    "gateway": "10.16.191.254",
                    "vlan_id": 6,
                    "network": "10.16.128.0/18"
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
                    "grisou-51.nancy.grid5000.fr"
                ],
                "cluster": "grisou",
                "role": "compute",
                "_c_nodes": [
                    "grisou-51.nancy.grid5000.fr"
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
                    "grisou-8.nancy.grid5000.fr"
                ],
                "cluster": "grisou",
                "role": "control",
                "_c_nodes": [
                    "grisou-8.nancy.grid5000.fr"
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
