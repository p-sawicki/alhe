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
    parser.add_argument('--mutation', '-m', metavar='R', type=float, default=0.3, help='Mutation factor')
    parser.add_argument('--xover', '-x', metavar='R', type=float, default=0.5, help='Crossover chance')
    parser.add_argument('--selection', '-sel', metavar='TYPE', type=str, default='exp', choices=['rand', 'exp'],
                        help='Selection type (rand / exp)')
    parser.add_argument('--succession', '-succ', metavar='TYPE', type=str, default='best', choices=['best', 'tourny'],
                        help='Succession type (best / tourny)')
    parser.add_argument('--multi-mode', dest='single_mode', action='store_false',
                        help='Whether to solve problem assuming that network support packets commutation')  # FIXME
    parser.add_argument('--output', metavar='DIR', dest='output_dir', type=str, default='output',
                        help='Name of directory to which results will be saved')
    parser.add_argument('--hide-plots', dest='show_plots', action='store_false',
                        help='Whether to display plots after final cycle of genetic algorithm')
    parser.add_argument('--quiet', '-q', dest='quiet', action='store_true', help='Run without printing anything')
    args = parser.parse_args()

    # Setup network model
    network = NetworkModel(args.model)
    network.parse()

    # Roll the genetic algorithm
    genetic = GeneticAlgorithm(network, args.population_size, args.epochs, args.mutation, args.single_mode,
                               args.xover, args.selection, args.succession)
    genetic.run(args.quiet)

    if not args.quiet:
        visualizer = NetworkVisualizer(args.output_dir, args.show_plots)
        genetic.result(visualizer)
        visualizer.showWindow()
        print('[i] Finished!')


if __name__ == '__main__':
    main()
