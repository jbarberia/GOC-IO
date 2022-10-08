# Contingency Description Data File
import re
from typing import List

# The keywords valid for this data format are:
# CONTINENCY
# END
# OPEN
# BRANCH
# FROM
# BUS
# TO
# CIRCUIT
# REMOVE
# UNIT

def parse_con(filename: str) -> List[dict]:
    """Read a file ands return an array with the information of the contingency.
    The `id` key belongs to:
        - `g` for generators
        - `e` for branches
        - `f` for transformers

    See table 3 for further details.

    The `event` key belongs to:
        - Generator contingency: "Generator Out-of-Service"
        - Branch contingency: "Branch Out-of-Service"

    Args:
        filename (str): path of the contingency file (*.con)

    Returns:
        List[dict]: array with the data of the contigency (event, name, id)

    Raises:
       NameError: Invalid filename extension 
    """
    if not filename.endswith(".con"):
        raise NameError("Invalid filename, `parse_con` works with *.con files")

    with open(filename) as io:
        file = io.read()

    contingencies = []
    contingencies_iterator = re.finditer(r"(?:CONTINGENCY).*?(?:END)", file, flags=re.S)
    for match in contingencies_iterator:
        contingency = match.group()
        name = re.search(r"(?<=CONTINGENCY ).*", contingency).group()
        generator_contingency = "REMOVE UNIT" in contingency
        branch_contingency = "OPEN BRANCH" in contingency

        if generator_contingency:
            bus_number = int(re.search(r"(?<=FROM BUS).[0-9]*", contingency).group())
            gen_id = re.search(r"(?<=REMOVE UNIT).[A-Z|0-9]*", contingency).group().strip().rjust(2, ' ')
            
            contingencies.append({
                "event": "Generator Out-of-Service",
                "name": name,
                "id": (bus_number, gen_id)
            })

        if branch_contingency:
            bus_from = int(re.search(r"(?<=FROM BUS).[0-9]*", contingency).group())
            bus_to = int(re.search(r"(?<=TO BUS).[0-9]*", contingency).group())
            ckt = re.search(r"(?<=CIRCUIT).[A-Z|0-9]*", contingency).group().strip().rjust(2, ' ')

            contingencies.append({
                "event": "Branch Out-of Service",
                "name": name,
                "id": (bus_from, bus_to, ckt)
            })
    
    return contingencies
