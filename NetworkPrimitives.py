from typing import List


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
    def __init__(self, name: str, source: str, target: str, value: float, paths: List[Link]):
        self.name = name
        self.source = source
        self.target = target
        self.value = value
        self.paths = paths

    def __str__(self) -> str:
        return f'Demand({self.name})["{self.source}" -> "{self.target}"]'
