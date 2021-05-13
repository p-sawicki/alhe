#!/usr/bin/env python3

import argparse

from Chromosome import Chromosome
from NetworkModel import *

"""
def init_pop(paths: dict) -> dict:
    population = {}
    for name in paths.keys():
        admissible_paths = paths[name]

        path_choice = [0] * len(admissible_paths)
        chosen_path = int(random.uniform(0, len(admissible_paths)))
        path_choice[chosen_path] = 1

        visits = []
        for _ in admissible_paths[chosen_path]:
            visits.append(int(random.uniform(0, 5)))

        population[name] = {
            'path_choice': path_choice,
            'visits': visits
        }
    return population"""


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
        for _ in range(self.epochs):
            # Select new population
            # TODO:

            # Reproduce the chosen ones
            # TODO:
            assert(len(self.population) == self.n)

            # Mutate
            for p in self.population:
                p.mutate(self.mutationFactor)

            # Save cost of the best member in population
            self.costHistory.append(
                min([p.objFunc() for p in self.population])
            )

    def result(self) -> None:
        pass


def main():
    parser = argparse.ArgumentParser(description='Solve network design problems using genetic algorithm')
    parser.add_argument('--model', '-f', metavar='FILE', type=str, default='polska.txt',
                        help='Path to file describing network model')
    parser.add_argument('--population-size', '-n', default=10,
                        metavar='N', type=int, help='Size of population used by genetic algorithm')
    parser.add_argument('--epochs', '-t', metavar='N', type=int, default=1000,
                        help='Number of cycles done before returning result')
    parser.add_argument('--mutation', type=float, default=0.1, help='Mutation factor')
    parser.add_argument('--multi-mode', dest='single_mode', action='store_false',
                        help='Whether to solve problem assuming that network support packets commutation')  # FIXME
    args = parser.parse_args()

    # Setup network model
    network = NetworkModel(args.model)
    network.parse()

    # Roll the genetic algorithm
    genetics = GeneticAlgorithm(network, args.population_size, args.epochs, args.mutation, args.single_mode)
    genetics.run()
    genetics.result()


if __name__ == '__main__':
    main()
