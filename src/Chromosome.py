import random
from typing import Dict, List, Tuple

from src.NetworkModel import NetworkModel


class Gene:
    """
    Gene consists of:
        path_choice: [0, 1, 0, ...] - which paths are used
        modules: [1, 2, 0, 3, ...] - how many modules were added to each link
    """
    def __init__(self, name: str, network: NetworkModel, singleMode: bool = True):
        self.name: str = name
        self.path_choices: List[float] = [random.uniform(0, 1)] * network.getDemand(name).pathsCount()
        self.modules: Dict[str, int] = {name: 0 for name in network.links}
        self.singleMode: bool = singleMode

        # Set a few modules in random places
        #for _ in range(2):
        #    randomKey = random.choice(list(self.modules.keys()))
        #    self.modules[randomKey] += random.randint(0, 1)

        self.normalize()

    def __str__(self) -> str:
        return f'Gene({self.name})[paths: {self.path_choices}; modules: {self.modules}]'

    def normalize(self) -> None:
        """
        Scale path_choice so that it always sums to 1
        """
        m = max(self.path_choices)
        s = sum(self.path_choices)

        if m == 0:
            self.path_choices = [1 if i == 0 else 0 for i in range(len(self.path_choices))]
            return

        if self.singleMode:
            mPos = self.path_choices.index(m)
            self.path_choices = [1 if i == mPos else 0 for i in range(len(self.path_choices))]
        else:
            self.path_choices = [c / s for c in self.path_choices]

    def totalVisits(self) -> int:
        """
        Return the number of visits required to setup all used modules
        """
        s = sum(self.modules.values())
        return s * 2


class Chromosome:
    """
    Chromosome consists of one gene per every demand
    """
    def __init__(self, network: NetworkModel, singleMode: bool = True):
        self.network = network
        self.singleMode = singleMode
        self.genes: Dict[str, Gene] = {
            demand.name: Gene(name=demand.name, network=network, singleMode=singleMode)
            for demand in network.demands.values()
        }

    def __str__(self) -> str:
        return f'Chromosome()[objFunc: {self.objFunc()}]'

    def totalLinksCapacity(self) -> Dict[str, float]:
        """
        Return the total capacity of each link
        """
        links: Dict[str, float] = {link.name: 0.0 for link in self.network.links.values()}
        for demand in self.network.demands.values():
            gene = self.genes[demand.name]
            for i, path in enumerate(demand.paths):
                for link in path:
                    links[link.name] += link.module_capacity * gene.modules[link.name]
        return links

    def modulesPerLink(self) -> Dict[str, int]:
        """
        Return the total number of modules installed on each link
        """
        links: Dict[str, int] = {link.name: 0 for link in self.network.links.values()}
        for demand in self.network.demands.values():
            for path in demand.paths:
                for link in path:
                    links[link.name] += self.genes[demand.name].modules[link.name]
        return links

    def calcDemands(self) -> Dict[str, float]:
        """
        For each link calculate the spare capacity
        """
        totalLinksCap = self.totalLinksCapacity()
        perLinkDemand: Dict[str, float] = {}
        perLinkRatio: Dict[str, float] = {}

        for demand in self.network.demands.values():
            gene = self.genes[demand.name]
            for i, path in enumerate(demand.paths):
                for link in path:
                    perLinkDemand[link.name] = perLinkDemand.get(link.name, 0.0) \
                                               + demand.value * gene.path_choices[i]

        for name in perLinkDemand:
            expected = perLinkDemand[name]
            current = totalLinksCap[name]
            perLinkRatio[name] = current - expected
        return perLinkRatio

    def objFunc(self) -> float:
        """
        Calculate the value of objective function which consists of
         1) checking that demands were met
         2) minimizing the number of visits
         3) minimizing the amount of wasted capacity
        """
        cost = 0.0

        # 1. check demands
        perLinkDemand = self.calcDemands()
        for name in perLinkDemand:
            diff = perLinkDemand[name]
            cost += abs(diff)

        # 2. count number of visits
        for gene in self.genes.values():
            cost += gene.totalVisits()

        # 3. count wasted network capacity
        # TODO:

        return cost

    def mutate(self, mutationFactor: float) -> None:
        """
        For each gene in chromosome, apply mutation algorithm with frequency
        controlled by @mutationFactor argument
        """
        for demandName in self.genes:
            if random.uniform(0, 1) > mutationFactor:
                continue

            gene = self.genes[demandName]

            # Mutate path_choices
            choicesVal = random.uniform(0, 1)
            choicesPos = random.randint(0, len(gene.path_choices) - 1)
            gene.path_choices[choicesPos] = choicesVal
            gene.normalize()

            # Mutate modules
            modulesVal = random.randint(0, 4)
            modulesPos = random.choice(list(gene.modules.keys()))
            gene.modules[modulesPos] = modulesVal

    @staticmethod
    def reproduce(parent1: 'Chromosome', parent2: 'Chromosome') -> Tuple['Chromosome', 'Chromosome']:
        """
        Trivial implementation of one point slice. For each gene, randomly select
        slice point for paths_choices and modules count
        """
        child1 = Chromosome(parent1.network, parent1.singleMode)
        child2 = Chromosome(parent2.network, parent2.singleMode)

        for demandName in child1.genes:
            gene1 = child1.genes[demandName]
            gene2 = child2.genes[demandName]

            slicePaths = random.randint(0, len(gene1.path_choices) - 1)
            p11 = gene1.path_choices[:slicePaths]
            p12 = gene1.path_choices[slicePaths:]
            p21 = gene2.path_choices[:slicePaths]
            p22 = gene2.path_choices[slicePaths:]
            gene1.path_choices = p11 + p22
            gene2.path_choices = p21 + p12

            sliceModules = random.randint(0, len(gene1.modules))
            linesNames = [n for n in gene1.modules]
            p11 = {k: v for k, v in gene1.modules.items() if k in linesNames[:sliceModules]}
            p12 = {k: v for k, v in gene1.modules.items() if k in linesNames[sliceModules:]}
            p21 = {k: v for k, v in gene2.modules.items() if k in linesNames[:sliceModules]}
            p22 = {k: v for k, v in gene2.modules.items() if k in linesNames[sliceModules:]}
            p11.update(p22)
            p12.update(p21)
            gene1.modules = p11
            gene2.modules = p12

            gene1.normalize()
            gene2.normalize()

            assert(len(gene1.path_choices) == len(gene2.path_choices))
            assert(len(gene1.modules) == len(gene2.modules))

        return child1, child2
