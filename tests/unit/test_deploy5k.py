import mock
import unittest
from execo import Host
from deploy5k import deploy
from deploy5k.error import MissingNetworkError

class TestConcretizeNetwork(unittest.TestCase):

    def setUp(self):
        self.resources = {
            "networks":[{
                "type": "kavlan",
                "site": "rennes",
                "role": "role1"
            }, {
                "type": "kavlan",
                "site": "rennes",
                "role": "role2"
            }]
        }

    def testact(self):
        networks = [
            { "site": "rennes", "vlan_id": 4},
            { "site": "rennes", "vlan_id": 5}
        ]
        c_resources = deploy.concretize_networks(self.resources, networks)
        self.assertEquals(networks[0], c_resources["networks"][0]["_c_vlan_id"])
        self.assertEquals(networks[1], c_resources["networks"][1]["_c_vlan_id"])

    def test_one_missing(self):
        networks = [
            { "site": "rennes", "vlan_id": 4},
        ]
        with self.assertRaises(MissingNetworkError):
            c_resources = deploy.concretize_networks(self.resources, networks)

    def test_not_order_dependent(self):
        networks_1 = [
            { "site": "rennes", "vlan_id": 4},
            { "site": "rennes", "vlan_id": 5}
        ]
        networks_2 = [
            { "site": "rennes", "vlan_id": 5},
            { "site": "rennes", "vlan_id": 4}
        ]
        c_resources_1 = deploy.concretize_networks(self.resources, networks_1)
        c_resources_2 = deploy.concretize_networks(self.resources, networks_2)
        self.assertItemsEqual(c_resources_1["networks"], c_resources_2["networks"])


class TestConcretizeNodes(unittest.TestCase):

    def setUp(self):
        self.resources = {
            "machines": [{
                "role": "compute",
                "nodes": 1,
                "cluster": "foocluster",
            }, {
                "role": "compute",
                "nodes": 1,
                "cluster": "barcluster",
            }],
        }

    def testact(self):
        nodes = [Host("foocluster-1"), Host("barcluster-2")]
        c_resources = deploy.concretize_nodes(self.resources, nodes)
        self.assertItemsEqual(c_resources["machines"][0]["_c_nodes"],
                              [Host("foocluster-1")])
        self.assertItemsEqual(c_resources["machines"][1]["_c_nodes"],
                              [Host("barcluster-2")])

    def test_one_missing(self):
        nodes = [Host("foocluster-1")]
        c_resources = deploy.concretize_nodes(self.resources, nodes)
        self.assertItemsEqual(c_resources["machines"][0]["_c_nodes"],
                              [Host("foocluster-1")])
        self.assertItemsEqual(c_resources["machines"][1]["_c_nodes"], [])


    def test_same_cluster(self):
        nodes = [Host("foocluster-1"), Host("foocluster-2")]
        self.resources["machines"][1]["cluster"] = "foocluster"
        c_resources = deploy.concretize_nodes(self.resources, nodes)
        self.assertItemsEqual(c_resources["machines"][0]["_c_nodes"],
                              [Host("foocluster-1")])
        self.assertItemsEqual(c_resources["machines"][1]["_c_nodes"], [Host("foocluster-2")])

    def test_not_order_dependent(self):
        nodes = [Host("foocluster-1"), Host("foocluster-2"), Host("foocluster-3")]
        self.resources["machines"][0]["nodes"] = 2
        c_resources_1 = deploy.concretize_nodes(self.resources, nodes)
        nodes = [Host("foocluster-2"), Host("foocluster-3"), Host("foocluster-1")]
        self.resources["machines"][0]["nodes"] = 2
        c_resources_2 = deploy.concretize_nodes(self.resources, nodes)

        self.assertItemsEqual(c_resources_1["machines"][0]["_c_nodes"],
                              c_resources_2["machines"][0]["_c_nodes"])
