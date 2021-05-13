from typing import List, Dict

import FileParser


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


class Link:
    """
    Class representing a connection between two cities
    """
    def __init__(self, name: str, source: str, target: str, moduleCap: float, moduleCost: float):
        self.name = name
        self.source = source
        self.target = target
        self.module_capacity = moduleCap
        self.module_cost = moduleCost

    def __str__(self) -> str:
        return f'Link({self.name})["{self.source}" -> "{self.target}"]'


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
        paths = {path['name']: path['paths'] for path in paths}

        for node in nodes:
            self.nodes[node['name']] = Node(**node)
        for link in links:
            self.links[link['name']] = Link(**link)
        for demand in demands:
            name = demand['name']
            self.demands[name] = Demand(**demand, paths=paths[name])

    def getDemand(self, name: str) -> Demand:
        return self.demands[name]

    def linksCount(self) -> int:
        return len(self.links)
