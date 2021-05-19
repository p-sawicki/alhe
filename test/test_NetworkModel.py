from unittest import TestCase

from src.NetworkModel import NetworkModel, Node, Link, Demand


class TestNetworkModel(TestCase):
    def test_parse(self):
        network = NetworkModel('./testModel.txt')
        network.parse()

        expectedNodes = {
            'Gdansk': Node('Gdansk', 18.60, 54.20),
            'Szczecin': Node('Szczecin', 14.50, 53.40),
            'Warsaw': Node('Warsaw', 21.00, 52.20),
            'Wroclaw': Node('Wroclaw', 16.90, 51.10)
        }
        expectedLinks = {
            'Link_0_1': Link('Link_0_1', 'Gdansk', 'Warsaw', [155.0, 622.0], [156.0, 468.0]),
            'Link_0_2': Link('Link_0_2', 'Gdansk', 'Szczecin', [155.0, 622.0], [156.0, 468.0]),
            'Link_2_3': Link('Link_2_3', 'Szczecin', 'Wroclaw', [131.0, 622.0], [156.0, 468.0]),
            'Link_3_1': Link('Link_3_1', 'Wroclaw', 'Warsaw', [155.0, 622.0], [112.0, 468.0]),
        }
        expectedDemands = {
            'Demand_0_1': Demand('Demand_0_1', 'Gdansk', 'Warsaw', 195.0, float('inf'), [
                [expectedLinks['Link_0_1']],
                [expectedLinks['Link_0_2'], expectedLinks['Link_2_3'], expectedLinks['Link_3_1']]
            ]),
            'Demand_0_2': Demand('Demand_0_2', 'Gdansk', 'Wroclaw', 158.0, float('inf'), [
                [expectedLinks['Link_0_1'], expectedLinks['Link_3_1']],
                [expectedLinks['Link_0_2'], expectedLinks['Link_2_3']]
            ]),
            'Demand_0_3': Demand('Demand_0_3', 'Gdansk', 'Szczecin', 174.0, float('inf'), [
                [expectedLinks['Link_0_2']],
                [expectedLinks['Link_0_1'], expectedLinks['Link_3_1'], expectedLinks['Link_2_3']]
            ]),
        }

        self.assertDictEqual(network.nodes, expectedNodes, "Incorrect nodes list")
        self.assertDictEqual(network.links, expectedLinks, "Incorrect links list")
        self.assertDictEqual(network.demands, expectedDemands, "Incorrect demands list")
