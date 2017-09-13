.. image:: https://badge.fury.io/py/deploy5k.svg
    :target: https://badge.fury.io/py/deploy5k

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
            "primary_network": "n1",
            "secondary_networks": ["n2"]
        }, {
            "role": "control",
            "nodes": 1,
            "cluster": "parasilo",
            "primary_network": "1",
            "secondary_networks": ["n2"]
        }],
        "networks": [{"type": "prod", "id": "1","role": "network_1", "site": "rennes"},
            {"type": "kavlan", "id": "n2", "roles": ["network_2", "network_3"],  "site": "rennes"}]
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
