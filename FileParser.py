"""
    FileParser.py - implementation of input file parser
    Using XML version of input data would be probably easier, but you need
    to find it prior to writing vast and complicated text parser
"""

from typing import Any, Dict, List


def parse(file_name: str) -> (List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]):
    """
    Parse text file with network description

    @param file_name - path to input text file
    returns dicts - nodes, links, demands, paths
    """
    with open(file_name, 'r') as f:
        text = f.read().split()

    nodes = []
    links = []
    demands = []
    paths = []

    i = 0
    while i < len(text):
        if text[i] == 'LINKS':
            i += 2  # skip open bracket
            while text[i] != ')':
                name = text[i]
                source = text[i + 2]
                target = text[i + 3]
                i += 10

                module_capacities = []
                module_costs = []
                while text[i] != ')':
                    module_capacities.append(float(text[i]))
                    module_costs.append(float(text[i + 1]))
                    i += 2

                links.append({
                    'name': name,
                    'source': source,
                    'target': target,
                    'moduleCap': module_capacities,
                    'moduleCost': module_costs
                })
                i += 1  # skip link-end close bracket
        elif text[i] == 'DEMANDS':
            i += 2  # skip open bracket
            while text[i] != ')':
                name = text[i]
                source = text[i + 2]
                target = text[i + 3]
                demand_value = float(text[i + 6])

                max_path_length = float('inf')
                if text[i + 7] != 'UNLIMITED':
                    max_path_length = float(text[i + 7])

                demands.append({
                    'name': name,
                    'source': source,
                    'target': target,
                    'value': demand_value,
                    'maxLen': max_path_length
                })
                i += 8
        elif text[i] == 'ADMISSIBLE_PATHS':
            i += 2  # skip open bracket
            while text[i] != ')':
                name = text[i]
                i += 2  # skip open bracket

                part = []
                while text[i] != ')':
                    i += 2  # skip path name and open bracket

                    path = []
                    while text[i] != ')':
                        path.append(text[i])
                        i += 1

                    part.append(path)
                    i += 1  # skip path-end close bracket
                i += 1  # skip demand-end close bracket
                paths.append({
                    'name': name,
                    'paths': part
                })
        elif text[i] == 'NODES':
            i += 2
            while text[i] != ')':
                name = text[i]
                lon = float(text[i + 2])
                lat = float(text[i + 3])

                nodes.append({
                    'name': name,
                    'lon': lon,
                    'lat': lat,
                })
                i += 5
        i += 1

    return nodes, links, demands, paths
