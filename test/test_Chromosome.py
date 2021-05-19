import random
from unittest import TestCase

from src.Chromosome import Chromosome
from src.NetworkModel import NetworkModel, Link, Demand, Node


class TestChromosome(TestCase):
    def setUp(self):
        random.seed(1024)
        self.assertEqual(random.randint(0, 1000), 816)

        self.network = NetworkModel('./testModel.txt')
        self.network.parse()


class TestReproductionSingleMode(TestChromosome):
    def setUp(self):
        super().setUp()
        self.chromosome1 = Chromosome(self.network)
        self.chromosome2 = Chromosome(self.network)

        self.child1, self.child2 = Chromosome.reproduce(self.chromosome1, self.chromosome2)

    def test_chromosome_configs(self):
        # Check that single_mode was preserved
        self.assertEqual(self.child1.singleMode, self.chromosome1.singleMode)
        self.assertEqual(self.child2.singleMode, self.chromosome2.singleMode)
        for gene in self.child1.genes.values():
            self.assertEqual(gene.singleMode, self.child1.singleMode)
        for gene in self.child2.genes.values():
            self.assertEqual(gene.singleMode, self.child2.singleMode)

    def test_genes_count(self):
        self.assertEqual(len(self.child1.genes), len(self.chromosome1.genes))
        self.assertEqual(len(self.child2.genes), len(self.chromosome2.genes))

        for gene in self.child1.genes.values():
            self.assertEqual(len(gene.modules), len(self.network.links))
            self.assertEqual(
                len(gene.path_choices),
                self.network.getDemand(gene.name).pathsCount()
            )
        for gene in self.child2.genes.values():
            self.assertEqual(len(gene.modules), len(self.network.links))
            self.assertEqual(
                len(gene.path_choices),
                self.network.getDemand(gene.name).pathsCount()
            )
