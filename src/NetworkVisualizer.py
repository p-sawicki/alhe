import os
import networkx as nx
from matplotlib import pyplot as plt
from typing import Any, Dict, List, Tuple, Optional

from src.NetworkModel import NetworkModel
from src.Chromosome import Chromosome


class NetworkVisualizer:
    def __init__(self, outputDir: str, showPlots: bool = True):
        self.outputDir = outputDir
        if not os.path.exists(self.outputDir):
            os.makedirs(self.outputDir)
        self.showPlots = showPlots

    def getPath(self, name: str) -> str:
        return os.path.join(self.outputDir, name)

    def displayPlot(self):
        if self.showPlots:
            plt.show()

    def drawNetworkModel(self, network: NetworkModel, chromosome: 'Chromosome'):
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

        plt.savefig(self.getPath('network_modules.png'))
        self.displayPlot()

    def drawObjFuncGraph(self, costHistory: List[float]):
        plt.clf()
        plt.plot(costHistory)
        plt.title('Value of objective function for each epoch')
        plt.xlabel('Epoch number')
        plt.ylabel('Cost')

        plt.savefig(self.getPath('objfunc.png'))
        self.displayPlot()

    def drawChangesHistory(self, changesHistory: List[int]):
        plt.clf()
        plt.plot(changesHistory)
        plt.title('Epochs since last change of objective function')
        plt.xlabel('Epoch number')
        plt.ylabel('Epoch since last change')

        plt.savefig(self.getPath('changes_history.png'))
        self.displayPlot()

    def drawTable(self, title: str, outName: str,
                  rows: Optional[List[str]],
                  columns: Optional[List[str]],
                  dataSet: List[List[Any]]):
        plt.clf()
        fig, ax = plt.subplots()
        fig.patch.set_visible(False)
        ax.axis('off')
        ax.axis('tight')

        ax.table(cellText=dataSet, rowLabels=rows, colLabels=columns, loc='center')
        fig.tight_layout()

        plt.title(title)
        plt.savefig(self.getPath(outName))
        self.displayPlot()

    def outputCSV(self, name: str, columnLabels: List[str], dataSet: List[List[Any]]):
        with open(self.getPath(name), 'w') as f:
            f.write(','.join(columnLabels))
            f.write('\n')

            for line in dataSet:
                f.write(','.join(map(str, line)))
                f.write('\n')
            f.write('\n')
