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

    r = Resources(resources)
    options = {
      "job_name": "test",
      "walltime": "01:00:00",
    }
    # This
    r.reserve(**options)
    r.deploy(**options)
    r.configure_network(**options)
    # Or this
    # r.launch(**options)

    r.get_roles()
    r.get_networks()
