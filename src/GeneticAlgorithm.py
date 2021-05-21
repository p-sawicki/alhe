from typing import Dict, List

from src.Chromosome import Chromosome
from src.NetworkModel import NetworkModel
from src.NetworkVisualizer import NetworkVisualizer


class GeneticAlgorithm:
    def __init__(self, network: NetworkModel, n: int, epochs: int, mutationFactor: int, singleMode: bool):
        self.network = network
        self.n = n
        self.epochs = epochs
        self.mutationFactor = mutationFactor
        self.singleMode = singleMode

        # Used for tracing algorithm progress
        self.costHistory: List[float] = []
        self.changesHistory: List[int] = []
        self.lastSamePos = 0
        self.lastSameVal = 0.0

        # Create initial population
        self.population = [Chromosome(network, singleMode) for _ in range(self.n)]

    def run(self) -> None:
        for i in range(self.epochs):
            print(f'[i] Running epoch {i}')

            # Select new population
            row: List[Chromosome] = sorted(self.population, key=lambda x: x.objFunc())
            self.costHistory.append(row[0].objFunc())
            chosenOnes = row[0:len(row) // 2]
            chosenOnesSize = len(chosenOnes)

            # Reproduce the chosen ones
            for a in range(0, chosenOnesSize):
                for b in range(a + 1, chosenOnesSize):
                    child1, _ = Chromosome.reproduce(chosenOnes[a], chosenOnes[b])

                    # Apply mutation to the newly created child
                    child1.mutate(self.mutationFactor)

                    chosenOnes.append(child1)

            chosenOnes = sorted(chosenOnes, key=lambda x: x.objFunc())
            self.population = chosenOnes[:self.n]
            assert (len(self.population) == self.n)

            # Check how we're doing
            same = self.lenOfSame(i, self.costHistory[-1])
            self.changesHistory.append(same)

        # Sort final population
        self.population = sorted(self.population, key=lambda x: x.objFunc())

    def lenOfSame(self, epoch: int, score: float) -> int:
        """
        Returns number of epochs that resulted in the same score
        """
        if self.lastSameVal != score:
            self.lastSameVal = score
            self.lastSamePos = epoch
        return epoch - self.lastSamePos

    def result(self, visualizer: NetworkVisualizer) -> None:
        """
        Output a lot of useful information to .csv files
        Also, take care of drawing mathplotlib graphs
        :param visualizer: reference to NetworkVisualizer class
        :return: None
        """
        visualizer.drawNetworkModel(self.network, self.population[0])
        visualizer.drawObjFuncGraph(self.costHistory)
        visualizer.drawChangesHistory(self.changesHistory)

        visualizer.outputCSV('cost_history.csv',
                             ['Epoch', 'Value'],
                             [[i, val] for i, val in enumerate(self.costHistory)]
                             )

        bestResult = self.population[0]
        linksNames = [link for link in self.network.links]
        modules = bestResult.modulesPerLink()
        visualizer.outputCSV('modules_per_link.csv',
                             ['Link name', 'Modules installed'],
                             [[name, modules[name]] for name in linksNames]
                             )

        demandsNames = [demand for demand in self.network.demands]
        visualizer.outputCSV('path_choices.csv',
                             ['Demand name'] + [f'Path_{i}' for i in range(10)],
                             [[name] + bestResult.genes[name].path_choices for name in demandsNames]
                             )

        visualizer.outputCSV('modules_per_link_per_demand.csv',
                             ['Demand name'] + [name for name in linksNames],
                             [
                                 [name] +
                                 [str(bestResult.genes[name].modules[linkName]) for linkName in linksNames]
                                 for name in demandsNames
                             ])

        if self.singleMode:
            paths: Dict[str, List[str]] = {}
            for name in demandsNames:
                pathNo = bestResult.genes[name].path_choices.index(1)
                paths[name] = [link.name for link in self.network.getDemand(name).paths[pathNo]]

            visualizer.outputCSV('links_per_demand.csv',
                                 ['Demand name'] + [f'Link_{i}' for i in range(8)],
                                 [[name] + paths[name] for name in demandsNames]
                                 )
        else:
            visualizer.outputCSV('link_per_demand.csv',
                                 ['Demand name', 0], [['Not applicable...', 0]])

        visualizer.outputCSV('summary.csv',
                             ['Parameter', 'Value'],
                             [
                                 ['Epochs count', self.epochs],
                                 ['Population size', self.n],
                                 ['Mutation factor', self.mutationFactor],
                                 ['Single mode', self.singleMode],
                                 ['Network size (nodes)', len(self.network.nodes)],
                                 ['Network size (links)', len(self.network.links)],
                                 ['Network size (demands)', len(self.network.demands)],
                                 ['Best score', bestResult.objFunc()]
                             ]
                             )
