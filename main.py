from parse import parse
import pprint

if __name__ == '__main__':
    links, demands, paths = parse('polska.txt')

    pp = pprint.PrettyPrinter(indent=1, width=160)
    pp.pprint(links)
    pp.pprint(demands)
    pp.pprint(paths)
