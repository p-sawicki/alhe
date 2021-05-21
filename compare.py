#!/usr/bin/env python3
import argparse
import multiprocessing as mp

from src.GeneticAlgorithm import GeneticAlgorithm
from src.NetworkModel import NetworkModel

def run(q : mp.Queue, net, pop, epochs, mut, single, x, sel, succ):
  alg = GeneticAlgorithm(net, pop, epochs, mut, single, x, sel, succ)
  q.put(alg.run(True))

def main():
  parser = argparse.ArgumentParser(description='Compare various configurations of the genetic algorithm')
  parser.add_argument('--repeat', '-r', metavar='N', type=int, default=32, help='Number of runs for each config')
  parser.add_argument('--epochs', '-t', metavar='N', type=int, default=1000,
                        help='Number of cycles done before returning result')
  parser.add_argument('--model', '-f', metavar='FILE', type=str, default='polska.txt',
                        help='Path to file describing network model')
  parser.add_argument('--log', '-l', metavar='FILE', type=str, default='log.csv', help='Path to log file')
  args = parser.parse_args()

  epochs = args.epochs
  population = [10, 100, 1000]
  mutation = [0.25, 0.5, 0.75]
  xover = [0.25, 0.5, 0.75]
  selection = ['rand', 'exp']
  succession = ['best', 'tourny']

  network = NetworkModel(args.model)
  network.parse()

  log = open(args.log, 'w')
  log.write('population; mutation factor; crossover chance; selection; succession; score\n')

  best = float('inf')
  params = ()
  for pop in population:
    for mut in mutation:
      for x in xover:
        for sel in selection:
          for succ in succession:
            procs : list[mp.Process] = []
            q = mp.Queue()

            avg = 0.0
            for i in range(args.repeat):
              procs.append(mp.Process(target=run, args=(q, network,
                pop, epochs, mut, True, x, sel, succ,)))
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
              params = (pop, mut, x, sel, succ)
  print('best params: {}, score: {}'.format(params, best))
  log.close()

if __name__ == '__main__':
  main()