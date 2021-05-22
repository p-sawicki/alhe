#!/usr/bin/env python3
import argparse
import multiprocessing as mp
import random

from src.GeneticAlgorithm import GeneticAlgorithm
from src.NetworkModel import NetworkModel


def run(q: mp.Queue, net, pop, epochs, mut, single, x, sel, succ):
    try:
        alg = GeneticAlgorithm(net, pop, epochs, mut, single, x, sel, succ)
        q.put(alg.run(True))
    except KeyboardInterrupt:
        # Don't care didn't ask plus you're a child
        # (disable traceback on Ctrl-C)
        pass


def main():
    parser = argparse.ArgumentParser(description='Compare various configurations of the genetic algorithm')
    parser.add_argument('--repeat', '-r', metavar='N', type=int, default=30, help='Number of runs for each config')
    parser.add_argument('--epochs', '-t', metavar='N', type=int, default=10000,
                        help='Number of cycles done before returning result')
    parser.add_argument('--model', '-f', metavar='FILE', type=str, default='polska.txt',
                        help='Path to file describing network model')
    parser.add_argument('--log', '-l', metavar='FILE', type=str, default='log.csv', help='Path to log file')
    parser.add_argument('--multi-mode', dest='single_mode', action='store_false',
                        help='Whether to solve problem assuming that network support packets commutation')
    args = parser.parse_args()

    epochs = args.epochs
    mode = args.single_mode
    selection = ['rand', 'exp']
    succession = ['best', 'tourny']

    network = NetworkModel(args.model)
    network.parse()

    log = open(args.log, 'w')
    log.write('population; mutation factor; crossover chance; selection; succession; score\n')

    best = float('inf')
    params = {}
    while True:
        try:
            for sel in selection:
                for succ in succession:
                    pop = random.randint(10, 1000) # population
                    mut = random.uniform(0, 1) # mutation factor
                    x = random.uniform(0, 1) # crossover chance

                    # Scale number of epochs according to population in order to achieve 
                    # similar run times for each test
                    ep = epochs // pop

                    procs: list[mp.Process] = []
                    q = mp.Queue()

                    avg = 0.0
                    for i in range(args.repeat):
                        procs.append(mp.Process(target=run, args=(q, network, pop, ep, mut, 
                                                                    mode,  x, sel, succ,)))
                        procs[i].start()

                    for i in range(args.repeat):
                        procs[i].join()
                        score = q.get()
                        log.write('{};{};{};{};{};{}\n'.format(pop, mut, x, sel, succ, score))
                        avg += score
                    avg /= args.repeat

                    print('[{}, {}, {}, {}, {}]: {}'.format(pop, mut, x, sel, succ, avg))

                    if avg < best:
                        best = avg
                        params = {  'population':       pop, 
                                    'mutation factor':  mut, 
                                    'crossover chance': x, 
                                    'selection mode':   sel, 
                                    'succession mode':  succ }
        except KeyboardInterrupt:
            break

    print('\nbest params: {}, score: {}'.format(params, best))
    log.close()


if __name__ == '__main__':
    main()
