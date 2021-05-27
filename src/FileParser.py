"""
    FileParser.py - implementation of input file parser
    Using XML version of input data would be probably easier, but you need
    to find it prior to writing vast and complicated text parser
"""
from typing import Any, Dict, List, Tuple


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


def loadSolution(file_name: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Load network solution provided in form of XML file. The specification of format
    can be found on SNDlib home page.
    Return the number of modules added to each link and routing for each demand
    """
    try:
        from lxml import etree as et
    except ImportError:
        print("[-] Failed to load solution - lxml module is not installed !!!")
        raise   # Hard to say what should be returned in such case - raise exception anyway

    linksModules = {}
    demandsFlows = {}

    tree = et.parse(file_name)
    root = tree.getroot()
    for topGroup in root:
        if topGroup.tag == '{http://sndlib.zib.de/solution}linkConfigurations':
            for linkConfiguration in topGroup:
                linkID = linkConfiguration.attrib['linkId']

                if len(linkConfiguration) > 0:
                    instModules = linkConfiguration[0]
                    capacity = float(instModules.find('{http://sndlib.zib.de/solution}capacity').text)
                    count = float(instModules.find('{http://sndlib.zib.de/solution}installCount').text)
                else:
                    capacity = 0
                    count = 0

                linksModules[linkID] = {
                    'capacity': capacity,
                    'count': count
                }
        elif topGroup.tag == '{http://sndlib.zib.de/solution}demandRoutings':
            for demandRouting in topGroup:
                demandID = demandRouting.get('demandId')

                flows = []
                for flowPath in demandRouting:
                    value = float(flowPath.find('{http://sndlib.zib.de/solution}flowPathValue').text)
                    path = []
                    for link in flowPath.find('{http://sndlib.zib.de/solution}routingPath'):
                        path.append(link.text)
                    flows.append((value, path))
                demandsFlows[demandID] = flows
        else:
            raise KeyError(f'Unknown XML tag found in solution file - "{topGroup.tag}"')

    return linksModules, demandsFlows


def saveSolution(fileName: str, linksModules: Dict[str, Any], demandsFlows: Dict[str, Any]):
    """
    Save computed solution to XML file compatible with SNDlib platform
    linksModules must be of form:
        {'LINK_0_1': {'capacity': 4.0, 'count': 2.0}, ...}
    demandsFlows must be of form:
        {'Demand_0_1': [(127.0, ['Link_1', 'Link_2', ...])], ...}
    """
    try:
        from lxml import etree as et
    except ImportError:
        print("[-] Failed to save solution - lxml module is not installed !!!")
        return

    root = et.Element("solution")
    root.attrib['xmlns'] = 'http://sndlib.zib.de/solution'
    root.attrib['version'] = '1.0'

    linkConfigs = et.Element('linkConfigurations')
    for linkName in linksModules:
        linkModules = linksModules[linkName]

        linkConfig = et.Element('linkConfiguration')
        linkConfig.attrib['linkId'] = linkName

        if linkModules['count'] > 0:
            instModules = et.Element('installedModule')
            capacity = et.Element('capacity')
            count = et.Element('installCount')

            capacity.text = str(linkModules['capacity'])
            count.text = str(linkModules['count'])
            instModules.append(capacity)
            instModules.append(count)
            linkConfig.append(instModules)

        linkConfigs.append(linkConfig)
    root.append(linkConfigs)

    demandRoutings = et.Element('demandRoutings')
    demandRoutings.attrib['state'] = 'NOS'
    for demandName in demandsFlows:
        flows = demandsFlows[demandName]

        demandRouting = et.Element('demandRouting', demandId=demandName)
        for flow in flows:
            flowPath = et.Element('flowPath')
            flowPathValue = et.Element('flowPathValue')
            flowPathValue.text = str(flow[0])

            routingPath = et.Element('routingPath')
            for linkName in flow[1]:
                link = et.Element('linkId')
                link.text = linkName
                routingPath.append(link)
            flowPath.append(flowPathValue)
            flowPath.append(routingPath)

            demandRouting.append(flowPath)
        demandRoutings.append(demandRouting)
    root.append(demandRoutings)

    et = et.ElementTree(root)
    et.write(fileName, pretty_print=True, xml_declaration=True, encoding='UTF-8')
