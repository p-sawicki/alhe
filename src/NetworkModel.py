import queue
from typing import List, Dict, Tuple

import src.FileParser as FileParser


class Node:
    """
    Class representing a city in the network graph
    """
    def __init__(self, name: str, lon: float, lat: float):
        self.name = name
        self.lon = lon
        self.lat = lat

    def __str__(self) -> str:
        return f'Node({self.name})[{self.lon}:{self.lat}]'

    def __eq__(self, other) -> bool:
        return self.name == other.name and self.lon == other.lon and self.lat == other.lat


class Link:
    """
    Class representing a connection between two cities
    """
    def __init__(self, name: str, source: str, target: str, moduleCap: List[float], moduleCost: List[float]):
        self.name = name
        self.source = source
        self.target = target
        self.module_capacity = moduleCap[-1]
        self.module_cost = moduleCost[-1]

    def __str__(self) -> str:
        return f'Link({self.name})["{self.source}" -> "{self.target}"]'

    def __eq__(self, other) -> bool:
        return all([
            getattr(self, field) == getattr(other, field)
            for field in ['name', 'source', 'target', 'module_capacity', 'module_cost']
        ])


class Demand:
    """
    Class representing a demand for the particular city combination
    """
    def __init__(self, name: str, source: str, target: str, value: float, maxLen: float, paths: List[List[Link]]):
        self.name = name
        self.source = source
        self.target = target
        self.value = value
        self.maxLen = maxLen
        self.paths = paths

    def __str__(self) -> str:
        return f'Demand({self.name})["{self.source}" -> "{self.target}"]'
    
    def __eq__(self, other) -> bool:
        return all([
            getattr(self, field) == getattr(other, field)
            for field in ['name', 'source', 'target', 'value', 'maxLen', 'paths']
        ])

    def pathsCount(self) -> int:
        return len(self.paths)


class NetworkModel:
    """
    Class representing whole communication network
    """
    def __init__(self, filename: str, k: int = 1):
        self.filename = filename
        self.nodes: Dict[str, Node] = {}
        self.links: Dict[str, Link] = {}
        self.demands: Dict[str, Demand] = {}
        self.k = k

    def parse(self) -> None:
        nodes, links, demands, paths = FileParser.parse(self.filename)

        for node in nodes:
            self.nodes[node['name']] = Node(**node)
        for link in links:
            self.links[link['name']] = Link(**link)
        if not paths:
            paths = self.generateAdmissiblePaths(demands)
        else:
            paths = {path['name']: [[self.links[x] for x in p] for p in path['paths']] for path in paths}

        for demand in demands:
            name = demand['name']
            self.demands[name] = Demand(**demand, paths=paths[name])

    def generateAdmissiblePaths(self, demands: List[Dict], maxPathsPerDemand: int = 3) -> Dict[str, List[List[Link]]]:
        """
        Generate admissible paths using BFS with max. number of found paths provided
        as 1st argument
        """
        edges: Dict[str, List[str]] = {nodeName: [] for nodeName in self.nodes.keys()}
        for link in self.links.values():
            edges[link.source].append(link.target)
            edges[link.target].append(link.source)

        linksByEdges: Dict[Tuple[str, str], Link] = {}
        for edgeA in edges:
            for edgeB in edges[edgeA]:
                linksByEdges[edgeA, edgeB] = [
                    link
                    for link in self.links.values()
                    if (link.source, link.target) == (edgeA, edgeB) or (link.source, link.target) == (edgeB, edgeA)
                ][0]

        def bfs(startNode: str, targetNode: str, maxPaths: int) -> List[List[Link]]:
            """
            Run BFS on `edges` graph, starting from @startNode to @targetNode. Stop
            when no more paths exist or more than maxPaths were found
            """
            result = []

            visited = set()
            nodesQueue = queue.Queue()
            nodesQueue.put((startNode, [startNode]))

            while not nodesQueue.empty() and len(result) < maxPaths:
                cur, path = nodesQueue.get()
                visited.add(cur)

                for node in edges[cur]:
                    if node == targetNode:
                        # Now convert list of nodes to list of links
                        foundPath = path + [node]
                        final = []
                        for i in range(0, len(foundPath) - 1):
                            final.append(linksByEdges[foundPath[i], foundPath[i+1]])
                        result.append(final)
                    elif node not in visited:
                        nodesQueue.put((node, path + [node]))
            return result[:maxPaths]

        # Run BFS for each demand
        foundPaths: Dict[str, List[List[Link]]] = {}
        for demand in demands:
            foundPaths[demand['name']] = bfs(demand['source'], demand['target'], maxPathsPerDemand)
        return foundPaths

    def getDemand(self, name: str) -> Demand:
        return self.demands[name]

    def linksCount(self) -> int:
        return len(self.links)
