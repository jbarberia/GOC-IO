import numpy as np
import re

def parse_rop(filename:str) -> dict:
    """Read a generator cost data file

    Args:
        filename (str): path of the generator cost file (*.rop)

    Returns:
        dict: mapping from `g` (generator identifier) to piecewise linear cost table

    Raises:
        NameError: Invalid filename extension 
    """
    if not filename.endswith(".rop"):
        raise NameError("Invalid filename, `parse_rop` works with *.rop files")

    with open(filename) as io:
        file = io.read()

    # Generator dispatch data
    raw_generator_dispatch_data = re.search(r'(?<=BEGIN GENERATOR DISPATCH DATA\n).*(?=0 / END OF GENERATOR DISPATCH DATA)', file, flags=re.S).group()
    generator_dispatch_data = {}
    for raw_row in raw_generator_dispatch_data.splitlines():
        row = raw_row.split(",")
        if len(row) != 4:
            continue
        g = int(row[0]), row[1].strip().rjust(2, ' ')
        dsptbl = int(row[3])
        generator_dispatch_data[g] = {
            "id": g,
            "dispatch_table": dsptbl
        }

    # Active power dispatch table
    raw_generator_dispatch_table = re.search(r'(?<=BEGIN ACTIVE POWER DISPATCH TABLES\n).*(?=0 / END OF ACTIVE POWER DISPATCH TABLES)', file, flags=re.S).group()
    generator_dispatch_table = {}
    for raw_row in raw_generator_dispatch_table.splitlines():
        row = raw_row.split(",")
        if len(row) != 7:
            continue
        tbl = int(row[0])
        ctbl = int(row[6])
        generator_dispatch_table[tbl] = {
            "table": tbl,
            "cost_curve_table": ctbl
        }

    # Piecewise linear cost curve tables
    raw_piece_wise_linear_cost = re.search(r'(?<=BEGIN PIECE-WISE LINEAR COST TABLES\n).*(?=0 / END OF PIECE-WISE LINEAR COST TABLES)', file, flags=re.S).group()
    piece_wise_linear_cost_table = {}

    lines_piece_wise_linear_cost = raw_piece_wise_linear_cost.splitlines()
    header = r"[0-9]*,.*,[0-9]*"

    current_line = 0
    while current_line < len(lines_piece_wise_linear_cost):
        line = lines_piece_wise_linear_cost[current_line]
        if re.match(header, line):
            row = line.split(",")
            cost_table = int(row[0])
            label = row[1].strip("'")
            n_points = int(row[2])
            x, y = [], []
            for i in range(1, n_points+1):
                current_line += 1
                line = lines_piece_wise_linear_cost[current_line]
                row = line.split(",")
                x.append(float(row[0]))
                y.append(float(row[1]))
            piece_wise_linear_cost_table[cost_table] = {
                "cost_table": cost_table,
                "label": label,
                "n_points": n_points,
                "x": x,
                "y": y,
                "coefficients": np.polyfit(x, y, 2).tolist(),
            }
        current_line += 1

    # mapping g -> linear cost
    generator_cost = {}
    for g in generator_dispatch_data:
        table = generator_dispatch_data[g]["dispatch_table"]
        cost_curve = generator_dispatch_table[table]["cost_curve_table"]
        generator_cost[g] = piece_wise_linear_cost_table[cost_curve]

    return generator_cost
