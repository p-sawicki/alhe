#!/usr/bin/env python3

import argparse

from src.GeneticAlgorithm import GeneticAlgorithm
from src.NetworkModel import NetworkModel
from src.NetworkVisualizer import drawNetworkModel, drawObjFuncGraph, drawChangesHistory


def main():
    parser = argparse.ArgumentParser(description='Solve network design problems using genetic algorithm')
    parser.add_argument('--model', '-f', metavar='FILE', type=str, default='polska.txt',
                        help='Path to file describing network model')
    parser.add_argument('--population-size', '-n', default=10,
                        metavar='N', type=int, help='Size of population used by genetic algorithm')
    parser.add_argument('--epochs', '-t', metavar='N', type=int, default=100,
                        help='Number of cycles done before returning result')
    parser.add_argument('--mutation', '-m', metavar='M', type=float, default=0.3, help='Mutation factor')
    parser.add_argument('--multi-mode', dest='single_mode', action='store_false',
                        help='Whether to solve problem assuming that network support packets commutation')  # FIXME
    args = parser.parse_args()

    # Setup network model
    network = NetworkModel(args.model)
    network.parse()

    # Roll the genetic algorithm
    genetic = GeneticAlgorithm(network, args.population_size, args.epochs, args.mutation, args.single_mode)
    genetic.run()
    genetic.result()

    # Draw results
    drawNetworkModel(network,
                     genetic.population[0],
                     title=f'Solution n={args.population_size} t={args.epochs} m={args.mutation}')
    drawObjFuncGraph(genetic.costHistory)
    drawChangesHistory(genetic.changesHistory)


if __name__ == '__main__':
    main()
