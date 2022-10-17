import os
import math
from copy import deepcopy
from .parser_con import parse_con
from .parser_inl import parse_inl
from .parser_raw import parse_raw
from .parser_rop import parse_rop

def parse_data(directory: str) -> dict:
    """return a mapping with the case info. The contingencies are given in a list in the `contingencies` keys.

    Args:
        directory (str): file directory with case.* files

    Returns:
        dict: network mapping
    """
    files = os.listdir(directory)
    contingencies, participation_factor, cost, network = False, False, False, False
    for file in files:
        fullpath = os.path.join(directory, file)

        if file.endswith(".con"):
            contingencies = parse_con(fullpath)

        if file.endswith(".inl"):
            participation_factor = parse_inl(fullpath)
        
        if file.endswith(".rop"):
            cost = parse_rop(fullpath)

        if file.endswith(".raw"):
            network = parse_raw(fullpath)

    if not contingencies:
        raise ValueError(f"*.con file does not found in {directory}")

    if not participation_factor:
        raise ValueError(f"*.inl file does not found in {directory}")

    if not cost:
        raise ValueError(f"*.rop file does not found in {directory}")
    
    if not network:
        raise ValueError(f"*.raw file does not found in {directory}")
        
    for gen in network["generators"]:
        network["generators"][gen]["cost"] = cost[gen]
        network["generators"][gen]["alpha_g"] = participation_factor[gen]["alpha_g"]

    network["contingencies"] = contingencies

    return network

def build_references(network: dict) -> dict:
    """bus to equipment mapping

    Args:
        network (dict): network data type from `parse_data`

    Returns:
        dict: refences in the form `bus_components` (bus -> components)
    """
    references = {}
    network = deepcopy(network)

    references["bus_generators"] = {i: [] for i in network["buses"]}
    for index in network["generators"]:
        references["bus_generators"][index[0]].append(index)
    
    references["bus_loads"] = {i: [i] if i in network["loads"].keys() else [] for i in network["buses"]}
    references["bus_fixed_shunts"] = {i: [i] if i in network["fixed_shunts"].keys() else [] for i in network["buses"]}
    references["bus_switched_shunts"] = {i: [i] if i in network["switched_shunts"].keys() else [] for i in network["buses"]}
  
    references["bus_lines_i"] = {i: [] for i in network["buses"]}
    references["bus_lines_j"] = {i: [] for i in network["buses"]}
    for index in network["lines"]:
        references["bus_lines_i"][index[0]].append(index)
        references["bus_lines_j"][index[1]].append(index)
    
    references["bus_transformers_i"] = {i: [] for i in network["buses"]}
    references["bus_transformers_j"] = {i: [] for i in network["buses"]}
    for index in network["lines"]:
        references["bus_transformers_i"][index[0]].append(index)
        references["bus_transformers_j"][index[1]].append(index)

    areas = set(network["buses"][i]["area"] for i in network["buses"])
    references["area_buses"] = {i: [] for i in areas}
    for index in network["buses"]:
        references["area_buses"][network["buses"][index]["area"]].append(index)

    return references


def get_solution(network: dict) -> str:
    """Get the base case solution according to item E in SCOPF problem formulation.
    If the network data has the contingency flag, returns the solution 2 file string.

    Args:
        network (dict): GOC1 dict type network
        network_id (int): id of the network (Default: 0 -> Base Case)

    Returns:
        str: Represetation of the solution
    """
    solution_str = []
    references = build_references(network)
    network["contingency"] = network.get("contingency", False)

    # Contingency section
    if network["contingency"]:
        solution_str.append("-- contingency")
        solution_str.append("label")
        solution_str.append(network["contingency"]["name"])

    # Bus section
    solution_str.append("-- bus section")
    solution_str.append("i, v (p.u.), theta (deg), bcs(MVAR at v = 1 p.u.)")
    for i in network["buses"]:
        bus = network["buses"][i]
        bcs = sum((network["switched_shunts"][j]["bs"] * network["s_base"] for j in references["bus_switched_shunts"][i]), start=0)
        bus_string = map(str, [i, bus["vm"], bus["va"]*180/math.pi, bcs])
        solution_str.append(", ".join(bus_string))

    # Generator section
    solution_str.append("-- generator section")
    solution_str.append("i, id, p (MW), q (MVAR)")
    for g in network["generators"]:
        i, id = g
        pg = network["generators"][g]["pg"] * network["s_base"]
        qg = network["generators"][g]["qg"] * network["s_base"]
        gen_string = map(str, [i, id, pg, qg])
        solution_str.append(", ".join(gen_string))

    # Delta section
    if network["contingency"]:
        solution_str.append("--delta section")
        solution_str.append("delta (MW)")
        solution_str.append(str(network["delta_k"] * network["s_base"]))

    return "\n".join(solution_str)
