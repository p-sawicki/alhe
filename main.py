#!/usr/bin/env python3
import argparse

from src.GeneticAlgorithm import GeneticAlgorithm
from src.NetworkModel import NetworkModel
from src.NetworkVisualizer import NetworkVisualizer


def main():
    parser = argparse.ArgumentParser(description='Solve network design problems using genetic algorithm')
    parser.add_argument('--model', '-f', metavar='FILE', type=str, default='polska.txt',
                        help='Path to file describing network model')
    parser.add_argument('--population-size', '-n', default=10, metavar='N', type=int,
                        help='Size of population used by genetic algorithm')
    parser.add_argument('--epochs', '-t', metavar='N', type=int, default=100,
                        help='Number of cycles done before returning result')
    parser.add_argument('--mutation', '-m', metavar='M', type=float, default=0.3, help='Mutation factor')
    parser.add_argument('--multi-mode', dest='single_mode', action='store_false',
                        help='Whether to solve problem assuming that network support packets commutation')  # FIXME
    parser.add_argument('--output', metavar='DIR', dest='output_dir', type=str, default='output',
                        help='Name of directory to which results will be saved')
    parser.add_argument('--hide-plots', dest='show_plots', action='store_false',
                        help='Whether to display plots after final cycle of genetic algorithm')
    args = parser.parse_args()

    # Setup network model
    network = NetworkModel(args.model)
    network.parse()

    # Roll the genetic algorithm
    genetic = GeneticAlgorithm(network, args.population_size, args.epochs, args.mutation, args.single_mode)
    genetic.run()

    # Draw results
    visualizer = NetworkVisualizer(args.output_dir, args.show_plots)
    genetic.result(visualizer)

    print('[i] Finished!')


if __name__ == '__main__':
    main()
