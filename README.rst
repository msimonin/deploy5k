.. code-block:: python

    from deploy5k.api import Resources
    import json
    import logging
    logging.basicConfig(level=logging.DEBUG)

    resources = {
        "machines": [{
            "role": "compute",
            "nodes": 1,
            "cluster": "parasilo",
            "primary_network": "network1",
            "secondary_networks": ["network2"]
        }, {
            "role": "control",
            "nodes": 1,
            "cluster": "parasilo",
            "primary_network": "network1",
            "secondary_networks": ["network2"]
        }],
        "networks": [{"type": "prod", "role": "network1", "site": "rennes"},
            {"type": "kavlan", "role": "network2", "site": "rennes"}]
    }

    r = Resources(resources)
    options = {
      "job_name": "test",
      "walltime": "01:00:00",
    #  "force_deploy": True
    }
    # This
    r.reserve(**options)
    r.deploy(**options)
    print(r.c_resources)
    r.configure_network(**options)
    # Or this
    # r.launch(**options)

    print(r.get_roles())
    print(r.get_networks())
