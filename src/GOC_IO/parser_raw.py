import re
import math
import warnings

# Mapping PSSE 34 components
HEADERKEYS = ["IC", "SBASE", "REV", "XFRRAT", "NXFRAT", "BASFRQ"]
BUSKEYS = ["I", "NAME", "BASKV", "IDE", "AREA", "ZONE", "OWNER", "VM", "VA", "NVHI", "NVLO", "EVHI", "EVLO"]
LOADKEYS = ["I", "ID", "STAT", "AREA", "ZONE", "PL", "QL", "IP", "IQ", "YP", "YQ", "OWNER", "SCALE", "INTRPT", "DGENP", "DGENQ", "DGENF"]
FIXEDSHUNTKEYS = ["I", "ID", "STATUS", "GL", "BL"]
GENERATORKEYS = [ "I", "ID", "PG", "QG", "QT", "QB", "VS","IREG", "MBASE", "ZR", "ZX", "RT", "XT", "GTAP","STAT", "RMPCT", "PT", "PB", "O1", "F1", "O2", "F2", "O3", "F3","O4", "F4", "WMOD", "WPF", "NREG"]
BRANCHKEYS = ["I", "J", "CKT", "R", "X", "B", "RATEA", "RATEB", "RATEC", "GI", "BI", "GJ", "BJ", "STAT", "MET", "LEN", "O1", "F1", "O2", "F2", "O3", "F3", "O4", "F4"]
SYSTEMSWITCHINGDEVICEKEYS = ["I", "J", "CKT", "X", "RATEA", "RATEB", "RATEC", "STAT", "NSTAT", "MET", "STYPE", "NAME"]
TRANSFORMERP1KEYS=["I", "J", "K", "CKT", "CW", "CZ", "CM", "MAG1", "MAG2", "NMETR", "NAME", "STAT", "O1", "F1", "O2", "F2", "O3", "F3", "O4", "F4", "VECGRP", "ZCOD"]
TRANSFORMERP2KEYS = ["R1-2", "X1-2", "SBASE1-2", "R2-3", "X2-3", "SBASE2-3", "R3-1", "X3-1", "SBASE3-1", "VMSTAR", "ANSTAR"]
TRANSFORMERL1KEYS = ["WINDV1", "NOMV1", "ANG1", "RATEA", "RATEB", "RATEC", "COD1", "CONT1", "RMA1", "RMI1", "VMA1", "VMI1", "NTP1", "TAB1", "CR1", "CX1", "CNXA1", "NOD1"]
TRANSFORMERL2KEYS = ["WINDV2", "NOMV2", "ANG2", "RATEA", "RATEB", "RATEC", "COD2", "CONT2", "RMA2", "RMI2", "VMA2", "VMI2", "NTP2", "TAB2", "CR2", "CX2", "CNXA2", "NOD2"]
TRANSFORMERL3KEYS = ["WINDV3", "NOMV3", "ANG3", "RATEA", "RATEB", "RATEC", "COD3", "CONT3", "RMA3", "RMI3", "VMA3", "VMI3", "NTP3", "TAB3", "CR3", "CX3", "CNXA3", "NOD3"]
AREAKEYS = ["I", "ISW", "PDES", "PTOL", "ARNAME"]
TWOTERMINALDCL1KEYS = ["NAME", "MDC", "RDC", "SETVL", "VSCHD", "VCMOD", "RCOMP", "DELTI", "METER", "DCVMIN", "CCCITMX", "CCCACC"]
TWOTERMINALDCL2KEYS = ["IPR", "NBR", "ANMXR", "ANMNR", "RCR", "XCR", "EBASR", "TRR", "TAPR", "TMXR", "TMNR", "STPR", "ICR", "IFR", "ITR", "IDR", "XCAPR", "NDR"]
TWOTERMINALDCL3KEYS=["IPI", "NBI", "ANMXI", "ANMNI", "RCI", "XCI", "EBASI", "TRI", "TAPI", "TMXI", "TMNI", "STPI", "ICI", "IFI", "ITI", "IDI", "XCAPI", "NDI"]
VSCDCLINEL1KEYS = ["NAME", "MDC", "RDC", "O1", "F1", "O2", "F2", "O3", "F3", "O4", "F4"]
VSCDCLINEL2KEYS = ["IBUS", "TYPE", "MODE", "DCSET", "ACSET", "ALOSS", "BLOSS", "MINLOSS", "SMAX", "IMAX", "PWF", "MAXQ", "MINQ", "VSREG", "RMPCT", "NREG"]
IMPEDANCECORRECTIONL1KEYS = ["I", "T1", "Re(F1)", "Im(F1)", "T2", "Re(F2)", "Im(F2)", "T3", "Re(F3)", "Im(F3)", "T4", "Re(F4)", "Im(F4)", "T5", "Re(F5)", "Im(F5)", "T6", "Re(F6)", "Im(F6)"]
IMPEDANCECORRECTIONL2KEYS = ["T7", "Re(F7)", "Im(F7)", "T8", "Re(F8)", "Im(F8)", "T9", "Re(F9)", "Im(F9)", "T10", "Re(F10)", "Im(F10)", "T11", "Re(F11)", "Im(F11)", "T12", "Re(F12)", "Im(F12)"]
MULTITERMINALDCL1KEYS = ["NAME","NCONV","NDCBS","NDCLN","MDC","VCONV","VCMOD","VCONVN"]
MULTITERMINALDCL2KEYS = ["IB", "N", "ANGMX", "ANGMN", "RC", "XC", "EBAS", "TR", "TAP", "TPMX", "TPMN", "TSTP", "SETVL", "DCPF", "MARG", "CNVCOD"]
MULTITERMINALDCL3KEYS = ["IDC","IB","AREA","ZONE","DCNAME","IDC2","RGRND","OWNER"]
MULTITERMINALDCL4KEYS = ["IDC","JDC","DCCKT","MET","RDC","LDC"]
MULTISECTIONLINEKEYS = ["I", "J", "'ID'", "MET", "DUM1", "DUM2", "DUM3", "DUM4", "DUM5", "DUM6", "DUM7", "DUM8", "DUM9"]
ZONEKEYS = ["I","ZONAME"]
INTERAREATRANSFERKEYS = ["ARFROM", "ARTO", "TRID", "PTRAN"]
OWNERKEYS = ["I", "OWNAME"]
FACTSKEYS = ["NAME","I","J","MODE","PDES","QDES","VSET","SHMX","TRMX","VTMN","VTMX","VSMX","IMX","LINX","RMPCT","OWNER","SET1","SET2","VSREF","FCREG","'MNAME'","NREG"]
SWITCHEDSHUNTKEYS = ["I", "MODSW", "ADJM", "ST", "VSWHI", "VSWLO", "SWREG", "RMPCT", "RMIDNT", "BINIT", "N1", "B1", "N2", "B2", "N3", "B3", "N4", "B4", "N5", "B5", "N6", "B6", "N7", "B7", "N8", "B8", "NREG"]
INDUCTIONMACHINEKEYS=["I", "'ID'", "ST", "SC", "DC", "AREA", "ZONE", "OWNER", "TC", "BC", "MBASE", "RATEKV", "PC", "PSET", "H", "A", "B", "D", "E", "RA", "XA", "XM", "R1", "X1", "R2", "X2", "X3", "E1", "SE1", "E2", "SE2", "IA1", "IA2", "XAMULT"]
GNEKEYS = [] # Not supported yet

DATA = {
    "BUS": BUSKEYS,
    "LOAD": LOADKEYS,
    "FIXED SHUNT": FIXEDSHUNTKEYS,
    "GENERATOR": GENERATORKEYS,
    "BRANCH": BRANCHKEYS,
    "SYSTEM SWITCHING DEVICE": SYSTEMSWITCHINGDEVICEKEYS,
    "TRANSFORMER": [TRANSFORMERP1KEYS, TRANSFORMERP2KEYS, TRANSFORMERL1KEYS, TRANSFORMERL2KEYS, TRANSFORMERL3KEYS],
    "AREA": AREAKEYS,
    "TWO-TERMINAL DC": [TWOTERMINALDCL1KEYS, TWOTERMINALDCL2KEYS, TWOTERMINALDCL3KEYS],
    "VSC DC LINE": [VSCDCLINEL1KEYS, VSCDCLINEL2KEYS],
    "IMPEDANCE CORRECTION": [IMPEDANCECORRECTIONL1KEYS, IMPEDANCECORRECTIONL2KEYS],
    "MULTI-TERMINAL DC": [MULTITERMINALDCL1KEYS, MULTITERMINALDCL2KEYS, MULTITERMINALDCL3KEYS, MULTITERMINALDCL4KEYS],
    "MULTI-SECTION LINE": MULTISECTIONLINEKEYS,
    "ZONE": ZONEKEYS,
    "INTER-AREA TRANSFER": INTERAREATRANSFERKEYS,
    "OWNER": OWNERKEYS,
    "FACTS": FACTSKEYS,
    "SWITCHED SHUNT": SWITCHEDSHUNTKEYS,
    "INDUCTION MACHINE": INDUCTIONMACHINEKEYS,
    "GNE": GNEKEYS,
    }
    
MULTILINECOMPONENTS = ["TRANSFORMER", "TWO-TERMINAL DC", "VSC DC LINE", "IMPEDANCE CORRECTION", "MULTI-TERMINAL DC"]

def read_case(filename: str) -> dict:
    """Read a *.raw file

    Args:
        filename (str): Name of psse *.raw file

    Returns:
        dict: PSSE 33 structured data

    Raises:
       NameError: Invalid filename extension 
    """
    if not filename.endswith(".raw"):
        raise NameError("Invalid filename, `read_case` works with *.raw files")
    case33 = {key: [] for key in DATA.keys()}
    key = None

    with open(filename) as f:
        for i, line in enumerate(f):
            # Get type of data
            type_data = get_type_of_data(line) if i != 2 else "BUS"
            if type_data == "END":
                break # End of file

            if type_data == "COMMENT":
                continue # Skip comment

            if type_data == "HEADER":
                parts = get_parts(line.split("/")[0], HEADERKEYS)
                case33["HEADER"] = parts
                continue

            if type_data: # Header of block data
                key = type_data
                continue

            # Populate dict if is in data block
            if key:
                if key not in MULTILINECOMPONENTS:
                    # Get parts and pad with None missing info
                    parts = get_parts(line, DATA[key])

                    # Add to the case
                    case33[key].append(parts)

                elif key == "TRANSFORMER":
                    components = []
                    for j, sublist in enumerate(DATA[key]):
                        parts = get_parts(line, sublist)
                        components.append(parts)
                        if j < 3:
                            line = next(f)
                        elif j == 3:
                            line = next(f) if components[0]["K"] != '0' else ""
                    # Append to case
                    case33[key].append(components)
                else:
                    components = []
                    for j, sublist in enumerate(DATA[key]):
                        parts = get_parts(line, sublist)
                        components.append(parts)
                        if j < len(DATA[key]) - 1:
                            line = next(f)
                    # Append to case
                    case33[key].append(components)
    return case33

def get_type_of_data(line):
    match_end = re.search(r"^Q", line)
    if match_end:
        return "END"

    match_comment = re.search(r"^@!", line)
    if match_comment:
        return "COMMENT"
    
    match_header = re.search(f"^0([^,]*,)([^,]*,)\s*33", line)
    if match_header:
        return "HEADER"

    match_data_type = re.search(r"(?<=BEGIN\s).*(?=\sDATA)", line)
    if match_data_type:
        return match_data_type.group()

    return None

def get_parts(line, data: list):
    parts = [part.strip() for part in line.split(",")]
    parts.extend([None] * (len(data) - len(parts)))
    component = {key: part for key, part in zip(data, parts)}
    return component

def parse_raw(filename: str) -> dict:
    """Representation of GOC 1 data format from a *.raw file

    Args:
        filename (str): Name of psse *.raw file

    Returns:
        dict: mapping according to SCOPF Problem Formulation
    """
    pass
    goc_case = {}
    case33 = read_case(filename)

    # Case identification data (C.2)
    goc_case["s_base"] = float(case33["HEADER"]["SBASE"])

    # Bus data from RAW (C.3)
    goc_case["buses"] = {}
    for raw_bus in case33["BUS"]:
        goc_bus = {
            "i": int(raw_bus["I"]),
            "area": int(raw_bus["AREA"]),
            "vm": float(raw_bus["VM"]),
            "va": float(raw_bus["VA"]),
            "nvhi": float(raw_bus["NVHI"]),
            "nvlo": float(raw_bus["NVLO"]),
            "evhi": float(raw_bus["EVHI"]),
            "evlo": float(raw_bus["EVLO"])
        }
        goc_case["buses"][int(raw_bus["I"])] = goc_bus

    # Load data from raw (C.4)
    goc_case["loads"] = {i: {"pl": 0, "ql": 0} for i in goc_case["buses"]}
    for raw_load in case33["LOAD"]:
        if int(raw_load["STAT"]) != 1:
            continue
        i = int(raw_load["I"])
        pl = float(raw_load["PL"])
        ql = float(raw_load["QL"])

        goc_case["loads"][i]["pl"] = goc_case["loads"][i]["pl"] + pl / goc_case["s_base"] 
        goc_case["loads"][i]["ql"] = goc_case["loads"][i]["ql"] + ql / goc_case["s_base"] 

    # Fixed shunt data from raw (C.5)
    goc_case["fixed_shunts"] = {i: {"gs": 0, "bs": 0} for i in goc_case["buses"]}
    for raw_shunt in case33["FIXED SHUNT"]:
        if int(raw_shunt["STATUS"]) != 1:
            continue
        i = int(raw_shunt["I"])
        gs = float(raw_shunt["GL"])
        bs = float(raw_shunt["BL"])

        goc_case["fixed_shunts"][i]["gs"] = goc_case["fixed_shunts"][i]["gs"] + gs / goc_case["s_base"]
        goc_case["fixed_shunts"][i]["bs"] = goc_case["fixed_shunts"][i]["bs"] + bs / goc_case["s_base"]

    # Generator data from raw (C.6)
    goc_case["generators"] = {}
    for raw_generator in case33["GENERATOR"]:
        if int(raw_generator["STAT"]) != 1:
            continue
        i = int(raw_generator["I"])
        g = i, raw_generator["ID"].strip("'").rjust(2, " ")
        pg = float(raw_generator["PG"]) / goc_case["s_base"]
        pghi = float(raw_generator["PT"]) / goc_case["s_base"]
        pglo = float(raw_generator["PB"]) / goc_case["s_base"]
        qg = float(raw_generator["QG"]) / goc_case["s_base"]
        qghi = float(raw_generator["QT"]) / goc_case["s_base"]
        qglo = float(raw_generator["QB"]) / goc_case["s_base"]

        goc_case["generators"][g] = {
            "g": g,
            "i": i,
            "pg": pg,
            "qg": qg,
            "qghi": qghi,
            "qglo": qglo,
            "pghi": pghi,
            "pglo": pglo
        }

    # Line data from raw (C.7)
    goc_case["lines"] = {}
    for raw_line in case33["BRANCH"]:
        if int(raw_line["STAT"]) != 1:
            continue
        bus_from = int(raw_line["I"])
        bus_to = int(raw_line["J"])
        ckt = raw_line["CKT"].strip("'").rjust(2, " ")
        e = (bus_from, bus_to, ckt)
        r = float(raw_line["R"])
        x = float(raw_line["X"])
        b = float(raw_line["B"])
        rate_a = float(raw_line["RATEA"]) / goc_case["s_base"]
        rate_c = float(raw_line["RATEC"]) / goc_case["s_base"]

        goc_case["lines"][e] = {
            "e": e,
            "i": bus_from,
            "j": bus_to,
            "g": r / (r**2 + x**2),
            "b": -x / (r**2 + x**2),
            "b_ch": b,
            "rate": rate_a,
            "rate_k": rate_c
        }

    # Transformer data from raw (C.8)
    goc_case["transformers"] = {}
    for raw_transformer in case33["TRANSFORMER"]:
        if int(raw_transformer[0]["STAT"]) != 1:
            continue
        if int(raw_transformer[0]["K"]) != 0:
            warnings.warn("Skip 3 winding transformer, GOC1 does not supoort this component")
            continue
        from_bus = int(raw_transformer[0]["I"])
        to_bus = int(raw_transformer[0]["J"])
        ckt = raw_transformer[0]["CKT"].strip("'").rjust(2, " ")
        f = (from_bus, to_bus, ckt)
        g_mag = float(raw_transformer[0]["MAG1"])
        b_mag = float(raw_transformer[0]["MAG2"])
        r = float(raw_transformer[1]["R1-2"])
        x = float(raw_transformer[1]["X1-2"])
        windv1 = float(raw_transformer[2]["WINDV1"])
        windv2 = float(raw_transformer[3]["WINDV2"])
        ang1 = float(raw_transformer[2]["ANG1"])
        rate_a = float(raw_transformer[2]["RATEA"]) / goc_case["s_base"]
        rate_c = float(raw_transformer[2]["RATEC"]) / goc_case["s_base"]

        goc_case["transformers"][f] = {
            "f": f,
            "i": from_bus,
            "j": to_bus,
            "g": r / (r**2 + x**2),
            "b": -x / (r**2 + x**2),
            "g_mag": g_mag,
            "b_mag": b_mag,
            "tap": windv1 / windv2,
            "shift": ang1 * 180 / math.pi,
            "rate": rate_a,
            "rate_k": rate_c
        }
    
    # switched shunt data from raw (C.9)
    goc_case["switched_shunts"] = {}
    for raw_shunt in case33["SWITCHED SHUNT"]:
        if int(raw_shunt["ST"]) != 1:
            continue
        i = int(raw_shunt["I"])
        bs = float(raw_shunt["BINIT"]) / goc_case["s_base"]
        b_values = [int(raw_shunt[f"N{x}"]) * float(raw_shunt[f"B{x}"]) for x in range(1, 9)]
        bshi = sum(max(0, b) for b in b_values)
        bslo = sum(min(0, b) for b in b_values)

        goc_case["switched_shunts"][i] = {
            "i": i,
            "bs0": bs,
            "bs": bs,
            "bshi": bshi,
            "bslo": bslo
        }

    return goc_case

