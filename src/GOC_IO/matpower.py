from itertools import chain

def to_matpower(network: dict, filename: str) -> None:
    """Writes a mpc version 1 file

    1. Do not export switched shunts
    2. Do not export magnetizing impedance in transformers

    Args:
        network (dict): GOC1 dict data
        filename (str): name of the file
    """
    mpc_name = "matpower_case"
    mpc_baseMVA = network["s_base"]

    mpc_bus_header = ["BUS I", "BUS TYPE", "PD", "QD", "GS", "BS", "BUS AREA", "VM", "VA", "BASE KV", "ZONE", "VMAX", "VMIN"]
    mpc_buses = []
    for bus in network["buses"].values():
        pd = network["loads"][bus["i"]]["pl"] * network["s_base"]
        qd = network["loads"][bus["i"]]["ql"] * network["s_base"]
        gs = network["fixed_shunts"][bus["i"]]["gs"] * network["s_base"]
        bs = network["fixed_shunts"][bus["i"]]["bs"] * network["s_base"]
        mpc_bus = {
            "BUS I": bus["i"],
            "BUS TYPE": bus["type"],
            "PD": pd,
            "QD": qd,
            "GS": gs,
            "BS": bs,
            "BUS AREA": bus["area"],
            "VM": bus["vm"],
            "VA": bus["va"],
            "BASE KV": bus["base_kv"],
            "ZONE": bus["area"],
            "VMAX": bus["nvhi"],
            "VMIN": bus["nvlo"],
        }
        mpc_buses.append(mpc_bus)

    mpc_gen_header = ["GEN BUS" ,"PG" ,"QG" ,"QMAX" ,"QMIN" ,"VG" ,"MBASE" ,"GEN STATUS" ,"PMAX" ,"PMIN"]
    mpc_gen_cost_header = ["MODEL", "STARTUP", "SHUTDOWN", "NCOST", "COST"]
    mpc_generators = []
    mpc_gen_costs = []
    for gen in network["generators"].values():
        mpc_gen = {
            "GEN BUS": gen["i"],
            "PG": gen["pg"],
            "QG": gen["qg"],
            "QMAX": gen["qghi"] * network["s_base"],
            "QMIN": gen["qglo"] * network["s_base"],
            "VG": gen["vg"],
            "MBASE": gen["m_base"],
            "GEN STATUS": 1,
            "PMAX": gen["pghi"] * network["s_base"],
            "PMIN": gen["pglo"] * network["s_base"],
        }
        mpc_generators.append(mpc_gen)
        cost = gen["cost"]
        mpc_cost = {
            "MODEL": 1,
            "STARTUP": 0,
            "SHUTDOWN": 0,
            "NCOST": len(cost["x"]),
            "COST": ", ".join([f"{y}, {x}" for y, x in zip(cost["y"], cost["x"])]),
        }
        mpc_gen_costs.append(mpc_cost)

    mpc_branch_header = ["F BUS", "T BUS", "BRR", "BRX", "BRB", "RATEA", "RATEB", "RATEC", "TAP", "SHIFT", "BRSTATUS"]
    mpc_branches = []
    for br in chain(network["lines"].values(), network["transformers"].values()):
        r = br["g"] / (br["g"]**2 + br["b"]**2)
        x = -br["b"] / (br["g"]**2 + br["b"]**2)
        mpc_branch = {
            "F BUS": br["i"],
            "T BUS": br["j"],
            "BRR": r,
            "BRX": x,
            "BRB": br.get("b_ch", 0),
            "RATEA": br["rate"] * network["s_base"],
            "RATEB": br["rate"] * network["s_base"],
            "RATEC": br["rate_k"] * network["s_base"],
            "TAP": br.get("tap", 0),
            "SHIFT": br.get("shift", 0),
            "BRSTATUS": 1,
        }
        mpc_branches.append(mpc_branch)

    
    with open(filename, "w") as io:
        io.writelines([
            f"function mpc = {mpc_name}\n",
            f"mpc.version = \'1\';\n",
            f"mpc.baseMVA = {mpc_baseMVA};\n",
        ])
    
        # Buses
        io.write("% {}\n".format("\t".join(mpc_bus_header)))
        io.write("mpc.bus = [\n")
        for bus in mpc_buses:
            string = "\t".join(str(bus[k]) for k in mpc_bus_header)
            io.write(f"{string};\n")
        io.write("];\n")
        
        # Generators
        io.write("% {}\n".format("\t".join(mpc_gen_header)))
        io.write("mpc.gen = [\n")
        for gen in mpc_generators:
            string = "\t".join(str(gen[k]) for k in mpc_gen_header)
            io.write(f"{string};\n")
        io.write("];\n")

        # Generators Cost
        io.write("% {}\n".format("\t".join(mpc_gen_cost_header)))
        io.write("mpc.gencost = [\n")
        for gen in mpc_gen_costs:
            string = "\t".join(str(gen[k]) for k in mpc_gen_cost_header)
            io.write(f"{string};\n")
        io.write("];\n")

        # Branches
        io.write("% {}\n".format("\t".join(mpc_branch_header)))
        io.write("mpc.branch = [\n")
        for br in mpc_branches:
            string = "\t".join(str(br[k]) for k in mpc_branch_header)
            io.write(f"{string};\n")
        io.write("];\n")
