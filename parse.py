def parse(file_name: str) -> (dict, dict, dict):
    """
    Parse text file with network description

    param file_name - path to input text file

    returns dicts - links, demands, paths
    """
    text = open(file_name, 'r').read().split()

    links = {}
    demands = {}
    paths = {}

    i = 0
    while i < len(text):
        if text[i] == 'LINKS':
            i += 2  # skip open bracket
            while text[i] != ')':
                name = text[i]
                source = text[i + 2]
                target = text[i + 3]
                pre_installed_capacity = float(text[i + 5])
                pre_installed_capacity_cost = float(text[i + 6])
                routing_cost = float(text[i + 7])
                setup_cost = float(text[i + 8])
                i += 10

                module_capacities = []
                module_costs = []
                while text[i] != ')':
                    module_capacities.append(float(text[i]))
                    module_costs.append(float(text[i + 1]))
                    i += 2

                links[name] = {
                    'source': source,
                    'target': target,
                    'pre_installed_capacity': pre_installed_capacity,
                    'pre_installec_capacity_cost': pre_installed_capacity_cost,
                    'routing_cost': routing_cost,
                    'setup_cost': setup_cost,
                    'module_capacities': module_capacities,
                    'module_costs': module_costs
                }
                i += 1  # skip link-end close bracket
        elif text[i] == 'DEMANDS':
            i += 2  # skip open bracket
            while text[i] != ')':
                name = text[i]
                source = text[i + 2]
                target = text[i + 3]
                routing_unit = float(text[i + 5])
                demand_value = float(text[i + 6])

                max_path_length = float('inf')
                if (text[i + 7] != 'UNLIMITED'):
                    max_path_length = float(text[i + 7])

                demands[name] = {
                    'source': source,
                    'target': target,
                    'routing_unit': routing_unit,
                    'demand_value': demand_value,
                    'max_path_length': max_path_length
                }
                i += 8
        elif text[i] == 'ADMISSIBLE_PATHS':
            i += 2  # skip open bracket
            while text[i] != ')':
                name = text[i]
                i += 2  # skip open bracket

                paths[name] = []
                while text[i] != ')':
                    i += 2  # skip path name and open bracket

                    path = []
                    while text[i] != ')':
                        path.append(text[i])
                        i += 1

                    paths[name].append(path)
                    i += 1  # skip path-end close bracket
                i += 1  # skip demand-end close bracket
        i += 1
    return links, demands, paths
