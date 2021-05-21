import copy
import math
import random
from typing import Dict, List, Tuple, Optional, Union

from src.NetworkModel import NetworkModel


class Gene:
    """
    Gene consists of:
        path_choice: [0, 1, 0, ...] - which paths are used
        modules: [1, 2, 0, 3, ...] - how many modules were added to each link
    """
    def __init__(self, name: str, network: NetworkModel, singleMode: bool = True):
        self.name: str = name
        self.path_choices: List[float] = [random.uniform(0, 1) for _ in range(network.getDemand(name).pathsCount())]
        self.modules: Dict[str, float] = {name: random.uniform(0, 1) for name in network.links}
        self.singleMode: bool = singleMode

        self.normalize()

    def __str__(self) -> str:
        return f'Gene({self.name})[paths: {self.path_choices}; modules: {self.modules}]'

    def normalize(self) -> None:
        """
        Scale path_choice so that it always sums to 1
        """
        assert (all([choice >= 0 for choice in self.path_choices]))

        m = max(self.path_choices)
        s = sum(self.path_choices)

        if m == 0:
            self.path_choices = [1 if i == 0 else 0 for i in range(len(self.path_choices))]
            return

        self.path_choices = [c / s for c in self.path_choices]

        if self.singleMode:
            avgPos = round(
                sum([
                    i * choice
                    for i, choice in enumerate(self.path_choices)
                ])
            )
            assert(0 <= avgPos < len(self.path_choices))

            self.path_choices = [1 if i == avgPos else 0 for i in range(len(self.path_choices))]


class Chromosome:
    """
    Chromosome consists of one gene per every demand
    """
    def __init__(self, network: NetworkModel, singleMode: bool = True, _skipGen: bool = False):
        self.network = network
        self.singleMode = singleMode

        if _skipGen:
            # _skipGen is used by __deepcopy__ to omit generation of initial genes,
            #  which are going to be overwritten anyway
            return

        self.genes: Dict[str, Gene] = {
            demand.name: Gene(name=demand.name, network=network, singleMode=singleMode)
            for demand in network.demands.values()
        }

    def __str__(self) -> str:
        return f'Chromosome()[objFunc: {self.objFunc()}]'

    def __deepcopy__(self, memo) -> object:
        """
        Override default deep-copy mechanism, so that network model is
        only referenced and not copied as well
        What could go wrong?
        """
        newObj = Chromosome(self.network, self.singleMode, True)
        newObj.genes = copy.deepcopy(self.genes)
        return newObj

    def totalLinksCapacity(self, modsPerLink: Optional[Dict[str, float]] = None) -> Dict[str, float]:
        """
        Return the total capacity of each link
        """
        if modsPerLink is None:
            modsPerLink = self.modulesPerLink()

        for link in self.network.links.values():
            modsPerLink[link.name] *= link.module_capacity
        return modsPerLink

    def modulesPerLink(self) -> Dict[str, int]:
        """
        Return the total number of modules installed on each link
        """
        links: Dict[str, Union[float, int]] = {link.name: 0.0 for link in self.network.links.values()}
        for demand in self.network.demands.values():
            gene = self.genes[demand.name]
            linksVisited = set()

            for i, path in enumerate(demand.paths):
                if gene.path_choices[i] <= 0.0:
                    continue

                for link in path:
                    if link.name in linksVisited:
                        continue
                    links[link.name] += gene.modules[link.name]
                    linksVisited.add(link.name)

        for link in links:
            links[link] = math.ceil(links[link])
        return links

    def calcDemands(self) -> Dict[str, float]:
        """
        For each link calculate the spare capacity
        """
        totalLinksCap = self.totalLinksCapacity()
        perLinkDemand: Dict[str, float] = {name: 0.0 for name in self.network.links}
        perLinkRatio: Dict[str, float] = {}

        for demand in self.network.demands.values():
            gene = self.genes[demand.name]
            for i, path in enumerate(demand.paths):
                for link in path:
                    perLinkDemand[link.name] += demand.value * gene.path_choices[i]

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
            if diff < 0:
                cost = 1e10
            else:
                cost += diff / 100

        # 2. count number of visits
        totalVisits = sum(self.modulesPerLink().values())
        cost += totalVisits * 10

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

            # Mutate modules
            modulesVal = random.uniform(0, 1)
            modulesPos = random.choice(list(gene.modules.keys()))
            gene.modules[modulesPos] = modulesVal

            if random.uniform(0, 1) > mutationFactor:
                continue

            # Mutate path_choices
            choicesVal = random.uniform(0, 1)
            choicesPos = random.randint(0, len(gene.path_choices) - 1)
            gene.path_choices[choicesPos] = choicesVal
            gene.normalize()

            if random.uniform(0, 1) > mutationFactor:
                continue

            # Add random zero to chromosome
            modulesPos = random.choice(list(gene.modules.keys()))
            gene.modules[modulesPos] = 0.0

    @staticmethod
    def reproduce(parent1: 'Chromosome', parent2: 'Chromosome') -> Tuple['Chromosome', 'Chromosome']:
        """
        Trivial implementation of one point slice. For each gene, randomly select
        slice point for paths_choices and modules count
        """
        child1 = copy.deepcopy(parent1)
        child2 = copy.deepcopy(parent2)

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
