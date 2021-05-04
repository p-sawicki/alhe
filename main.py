from parse import parse
import pprint
import random
import math


def obj_func(population: dict, links: dict, demands: dict, paths: dict) -> float:
    cost = 0.0
    link_capacity = {}
    for link in links.keys():
        link_capacity[link] = 0.0

    for demand in demands.keys():
        path_choice = population[demand]['path_choice']
        req_capacity = demands[demand]['demand_value']

        for i in range(len(path_choice)):
            if path_choice[i] != 0:
                chosen = i

        links_visited = paths[demand][chosen]

        for i in range(len(links_visited)):
            link = links_visited[i]
            visits = population[demand]['visits'][i]

            setup_cost = links[link]['setup_cost']
            added_capacity = links[link]['module_capacities'][0]

            cost += setup_cost * visits
            total_capacity = added_capacity * visits
            link_capacity[link] += total_capacity - req_capacity

    for link in links.keys():
        added_capacity = links[link]['module_capacities'][0]
        setup_cost = links[link]['setup_cost']

        if link_capacity[link] < 0.0:
            req_visits = -link_capacity[link] / added_capacity
            cost += setup_cost * math.ceil(req_visits)

    return cost


def init_pop(paths: dict) -> dict:
    population = {}
    for name in paths.keys():
        admissible_paths = paths[name]

        path_choice = [0] * len(admissible_paths)
        chosen_path = int(random.uniform(0, len(admissible_paths)))
        path_choice[chosen_path] = 1

        visits = []
        for _ in admissible_paths[chosen_path]:
            visits.append(int(random.uniform(0, 5)))

        population[name] = {
            'path_choice': path_choice,
            'visits': visits
        }
    return population


if __name__ == '__main__':
    links, demands, paths = parse('polska.txt')
    initial = init_pop(paths)
    cost = obj_func(initial, links, demands, paths)

    pp = pprint.PrettyPrinter(indent=1, width=160)
    pp.pprint(initial)
    print(cost)
