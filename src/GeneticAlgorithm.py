from src.Chromosome import Chromosome
from src.NetworkModel import NetworkModel


class GeneticAlgorithm:
    def __init__(self, network: NetworkModel, n: int, epochs: int, mutationFactor: int, singleMode: bool):
        self.network = network
        self.n = n
        self.epochs = epochs
        self.mutationFactor = mutationFactor
        self.costHistory = []

        # Create initial population
        self.population = [Chromosome(network, singleMode) for _ in range(self.n)]

    def run(self) -> None:
        for i in range(self.epochs):
            print(f'[i] Running epoch {i}')

            # Select new population
            # TODO: Maybe do it wisely
            row = sorted(self.population, key=lambda x: x.objFunc())
            chosenOnes = row[0:len(row) // 2]

            # Reproduce the chosen ones
            self.population = chosenOnes
            for j in range(0, len(chosenOnes)):
                child1, _ = Chromosome.reproduce(chosenOnes[0], chosenOnes[j])
                self.population.append(child1)
            assert(len(self.population) == self.n)

            # Mutate
            for p in self.population:
                p.mutate(self.mutationFactor)

            # Save cost of the best member in population
            self.costHistory.append(
                min([p.objFunc() for p in self.population])
            )

        # Sort final population
        self.population = sorted(self.population, key=lambda x: x.objFunc())

    def result(self) -> None:
        print(self.costHistory)
        print(self.population[0].modulesPerLink())
