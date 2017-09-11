from deploy5k import utils
from deploy5k.error import MissingNetworkError
from deploy5k.schema import KAVLAN
from execo import Host
from execo_g5k import api_utils as api
import copy
import mock
import unittest
import execo_g5k as ex5
class TestMountNics(unittest.TestCase):

    def test_exact(self):
        desc = {
            "cluster": "foocluster",
            "_c_nodes": ["foocluster-1", "foocluster-2"],
            "secondary_networks": ["network_1", "network_2"]
        }
        networks = [
            {
                "type": KAVLAN,
                "role": "network_1",
                "site": "rennes",
                "_c_network": {"vlan_id": 4, "site": "rennes"}
            },
            {
                "type": KAVLAN,
                "role": "network_2",
                "site": "rennes",
                "_c_network": {"vlan_id": 5, "site": "rennes"}},
        ]
        utils.get_cluster_interfaces = mock.Mock(return_value=["eth0", "eth1"])
        ex5.get_cluster_site = mock.Mock(return_value="rennes")
        api.set_nodes_vlan = mock.Mock()
        utils._mount_secondary_nics(desc, networks)
        self.assertItemsEqual([("eth0", "network_1"), ("eth1", "network_2")], desc["_c_nics"])

class TestConcretizeNetwork(unittest.TestCase):

    def setUp(self):
        self.resources = {
            "networks":[{
                "type": KAVLAN,
                "site": "rennes",
                "role": "role1"
            }, {
                "type": KAVLAN,
                "site": "rennes",
                "role": "role2"
            }]
        }
        ex5.get_resource_attributes = mock.Mock(return_value={'kavlans': {'4': {}, '5': {}}})

    def test_act(self):
        networks = [
            { "site": "rennes", "vlan_id": 4},
            { "site": "rennes", "vlan_id": 5}
        ]
        utils.concretize_networks(self.resources, networks)
        self.assertEquals(networks[0], self.resources["networks"][0]["_c_network"])
        self.assertEquals(networks[1], self.resources["networks"][1]["_c_network"])

    def test_one_missing(self):
        networks = [
            { "site": "rennes", "vlan_id": 4},
        ]
        with self.assertRaises(MissingNetworkError):
            utils.concretize_networks(self.resources, networks)

    def test_not_order_dependent(self):
        networks_1 = [
            { "site": "rennes", "vlan_id": 4},
            { "site": "rennes", "vlan_id": 5}
        ]
        networks_2 = [
            { "site": "rennes", "vlan_id": 5},
            { "site": "rennes", "vlan_id": 4}
        ]
        resources_1 = copy.deepcopy(self.resources)
        resources_2 = copy.deepcopy(self.resources)
        utils.concretize_networks(resources_1, networks_1)
        utils.concretize_networks(resources_2, networks_2)
        self.assertItemsEqual(resources_1["networks"], resources_2["networks"])


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

    def test_exact(self):
        nodes = [Host("foocluster-1"), Host("barcluster-2")]
        utils.concretize_nodes(self.resources, nodes)
        self.assertItemsEqual(self.resources["machines"][0]["_c_nodes"],
                              ["foocluster-1"])
        self.assertItemsEqual(self.resources["machines"][1]["_c_nodes"],
                              ["barcluster-2"])

    def test_one_missing(self):
        nodes = [Host("foocluster-1")]
        utils.concretize_nodes(self.resources, nodes)
        self.assertItemsEqual(self.resources["machines"][0]["_c_nodes"],
                              ["foocluster-1"])
        self.assertItemsEqual(self.resources["machines"][1]["_c_nodes"], [])


    def test_same_cluster(self):
        nodes = [Host("foocluster-1"), Host("foocluster-2")]
        self.resources["machines"][1]["cluster"] = "foocluster"
        utils.concretize_nodes(self.resources, nodes)
        self.assertItemsEqual(self.resources["machines"][0]["_c_nodes"],
                              ["foocluster-1"])
        self.assertItemsEqual(self.resources["machines"][1]["_c_nodes"], ["foocluster-2"])

    def test_not_order_dependent(self):
        nodes = [Host("foocluster-1"), Host("foocluster-2"), Host("foocluster-3")]
        self.resources["machines"][0]["nodes"] = 2
        resources_1 = copy.deepcopy(self.resources)
        utils.concretize_nodes(resources_1, nodes)
        nodes = [Host("foocluster-2"), Host("foocluster-3"), Host("foocluster-1")]
        resources_2 = copy.deepcopy(self.resources)
        resources_2["machines"][0]["nodes"] = 2
        utils.concretize_nodes(resources_2, nodes)

        self.assertItemsEqual(resources_1["machines"][0]["_c_nodes"],
                              resources_2["machines"][0]["_c_nodes"])
