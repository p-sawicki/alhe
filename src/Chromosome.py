import copy
import math
import random
from typing import Dict, List, Tuple, Union

from src.FileParser import saveSolution
from src.NetworkModel import NetworkModel


class Gene:
    """
    Gene consists of:
        path_choice: [0, 1, 0, ...] - which paths are used
    """

    def __init__(self, name: str, network: NetworkModel, singleMode: bool = True, _skipGen: bool = False):
        self.name: str = name
        self.network = network
        self.singleMode: bool = singleMode

        if not _skipGen:
            self.path_choices: List[float] = [random.uniform(0, 1) for _ in range(network.getDemand(name).pathsCount())]
            self.normalize()

    def __str__(self) -> str:
        return f'Gene({self.name})[paths: {self.path_choices}]'

    def __deepcopy__(self, memo) -> 'Gene':
        """
        When creating deepcopy of this class, avoid unnecessary copying of
        network attribute - it's huge and the same for all instances of this class
        """
        newObj = Gene(self.name, self.network, self.singleMode, _skipGen=True)
        newObj.path_choices = copy.deepcopy(self.path_choices)
        return newObj

    def getCapacity(self) -> Dict[str, float]:
        """
        Return the number of capacity units required to satisfy demands for
        selected @path_choice
        """
        links: Dict[str, float] = {name: 0.0 for name in self.network.links}

        demandValue = self.network.getDemand(self.name).value
        for i, path_choice in enumerate(self.path_choices):
            demandPart = demandValue * path_choice
            for link in self.network.getDemand(self.name).paths[i]:
                links[link.name] += demandPart
        return links

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
            assert (0 <= avgPos < len(self.path_choices))

            self.path_choices = [1 if i == avgPos else 0 for i in range(len(self.path_choices))]


class Chromosome:
    """
    Chromosome consists of one gene per every demand
    """

    def __init__(self, network: NetworkModel, singleMode: bool = True, _skipGen: bool = False, k: int = 1):
        self.network = network
        self.singleMode = singleMode
        self.k = k

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
        newObj = Chromosome(self.network, self.singleMode, True, self.k)
        newObj.genes = copy.deepcopy(self.genes)
        return newObj

    def saveToXML(self, filename: str):
        """
        Save chromosome to XML file compatible with SNDlib platform
        """
        if not self.singleMode:
            raise NotImplementedError('SaveToXML support only single-mode chromosomes')

        modsPerLink = self.modulesPerLink()
        linkModules = {}
        for link in modsPerLink:
            linkModules[link] = {
                'count': modsPerLink[link],
                'capacity': self.network.links[link].module_capacity
            }

        demandsFlow = {}
        for demandName in self.network.demands:
            gene = self.genes[demandName]
            path = self.network.getDemand(demandName).paths[gene.path_choices.index(1)]
            demandsFlow[demandName] = (
                self.network.getDemand(demandName).value,
                [link.name for link in path]
            )
        saveSolution(filename, linkModules, demandsFlow)

    def totalLinksCapacity(self) -> Dict[str, float]:
        """
        Return the total capacity of each link
        """
        capPerLink: Dict[str, float] = {link: 0.0 for link in self.network.links}
        for gene in self.genes.values():
            geneCap = gene.getCapacity()
            for linkName in self.network.links:
                capPerLink[linkName] += geneCap[linkName]

        return capPerLink

    def modulesPerLink(self, ceil: bool = True) -> Dict[str, int]:
        """
        Return the total number of modules installed on each link
        """
        links: Dict[str, Union[float, int]] = {link.name: 0.0 for link in self.network.links.values()}

        capPerLink = self.totalLinksCapacity()
        for linkName, link in self.network.links.items():
            links[linkName] += capPerLink[linkName] / link.module_capacity

        if ceil:
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
            modCap = self.network.links[name].module_capacity
            current = math.ceil(totalLinksCap[name] / modCap) * modCap
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
        cost += sum(perLinkDemand.values()) / 100

        # 2. count number of visits
        totalVisits = sum(self.modulesPerLink().values())
        cost += totalVisits * 10

        # 3. count wasted network capacity
        finalModulesCount = self.modulesPerLink()
        for linkName in finalModulesCount:
            cap = finalModulesCount[linkName] * self.network.links[linkName].module_capacity
            div = math.ceil(cap / self.k)
            wasted = div * self.k - cap
            cost += wasted / 10

            assert (self.k != 1 or wasted == 0)  # For k == 1 wasted should be always 0

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
            choicesVal = random.uniform(0, 2)
            choicesPos = random.randint(0, len(gene.path_choices) - 1)
            gene.path_choices[choicesPos] = choicesVal
            gene.normalize()

    @staticmethod
    def reproduce(parent1: 'Chromosome', parent2: 'Chromosome', xoverMode) -> 'Chromosome':
        """
        Trivial implementation of one point slice. For each gene, randomly select
        slice point for paths_choices and modules count
        """
        child = copy.deepcopy(parent1)

        if xoverMode == 'hor-slice':
            demandsNames = list(parent1.genes.keys())
            slicePos = random.randint(0, len(demandsNames) - 1)

            for name in demandsNames[:slicePos]:
                child.genes[name].path_choices = copy.deepcopy(parent1.genes[name].path_choices)
            for name in demandsNames[slicePos:]:
                child.genes[name].path_choices = copy.deepcopy(parent2.genes[name].path_choices)
        else:
            for demandName in parent1.genes:
                gene1 = parent1.genes[demandName]
                gene2 = parent2.genes[demandName]
                childGene = child.genes[demandName]
                size = len(gene1.path_choices)

                if xoverMode == 'avg':
                    childGene.path_choices = [
                        (gene1.path_choices[i] + gene2.path_choices[i]) / 2 for i in range(size)]
                elif xoverMode == 'vert-slice':
                    slicePoint = random.randint(0, size)
                    childGene.path_choices[:slicePoint] = gene1.path_choices[:slicePoint]
                    childGene.path_choices[slicePoint:] = gene2.path_choices[slicePoint:]
                else:
                    raise ValueError('Crossover mode must be one of the following: avg, vert-slice, hor-slice')
                childGene.normalize()

        return child
