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
                i += 2  # skip open bracket

                source = text[i]
                i += 1

                target = text[i]
                i += 2  # skip close bracket

                pre_installed_capacity = float(text[i])
                i += 1

                pre_installed_capacity_cost = float(text[i])
                i += 1

                routing_cost = float(text[i])
                i += 1

                setup_cost = float(text[i])
                i += 2  # skip open bracket

                module_capacities = []
                module_costs = []
                while text[i] != ')':
                    module_capacities.append(float(text[i]))
                    i += 1

                    module_costs.append(float(text[i]))
                    i += 1

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
                i += 2  # skip open bracket

                source = text[i]
                i += 1

                target = text[i]
                i += 2  # skip close bracket

                routing_unit = float(text[i])
                i += 1

                demand_value = float(text[i])
                i += 1

                max_path_length = float('inf')
                if (text[i] != 'UNLIMITED'):
                    max_path_length = float(text[i])

                demands[name] = {
                    'source': source,
                    'target': target,
                    'routing_unit': routing_unit,
                    'demand_value': demand_value,
                    'max_path_length': max_path_length
                }
                i += 1
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
