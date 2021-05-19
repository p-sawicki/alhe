from typing import List

from src.Chromosome import Chromosome
from src.NetworkModel import NetworkModel


class GeneticAlgorithm:
    def __init__(self, network: NetworkModel, n: int, epochs: int, mutationFactor: int, singleMode: bool):
        self.network = network
        self.n = n
        self.epochs = epochs
        self.mutationFactor = mutationFactor
        self.costHistory: List[float] = []

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
            assert(len(self.population) == self.n)

        # Sort final population
        self.population = sorted(self.population, key=lambda x: x.objFunc())

    def result(self) -> None:
        print(self.costHistory)
        print(self.population[0].modulesPerLink())
        for name, gene in self.population[0].genes.items():
            print(f'\t{name} - {gene.path_choices}')
