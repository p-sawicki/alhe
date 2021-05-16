import networkx as nx
from matplotlib import pyplot as plt
from typing import Dict, List, Tuple

from src.NetworkModel import NetworkModel
from src.Chromosome import Chromosome


def drawNetworkModel(network: NetworkModel, chromosome: 'Chromosome', title: str):
    G = nx.Graph()
    edgeLabels: Dict[Tuple[str, str], int] = {}
    modsPerLink = chromosome.modulesPerLink()

    for name, node in network.nodes.items():
        G.add_node(name, pos=(node.lon - 14, node.lat - 50))
    for link in network.links.values():
        G.add_edge(link.source, link.target)
        edgeLabels[(link.source, link.target)] = modsPerLink[link.name]

    pos = nx.get_node_attributes(G, 'pos')

    nx.draw(G, pos, with_labels=True)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edgeLabels, font_color='red')

    plt.show()


def drawObjFuncGraph(costHistory: List[float]):
    plt.plot(costHistory)
    plt.ylabel('Cost history')
    plt.show()
