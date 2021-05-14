import networkx as nx
from matplotlib import pyplot as plt

from NetworkModel import NetworkModel


def drawNetworkModel(network: NetworkModel):
    G = nx.Graph()

    for name, node in network.nodes.items():
        G.add_node(name, pos=(node.lon - 14, node.lat - 50))
    for link in network.links.values():
        G.add_edge(link.source, link.target)

    pos = nx.get_node_attributes(G, 'pos')

    nx.draw(G, pos, with_labels=True)
    plt.show()


