# python -m pip install . && python -m pytest ./tests/runtests.py
import pytest
import GOC_IO
from GOC_IO import parse_con, parse_inl, parse_rop, parse_raw

def test_parser_con():
    contingencies = parse_con("./tests/scenario_1/case.con")[-1]
    assert contingencies == {'event': 'Branch Out-of-Service', 'name': 'T_000497JASPER32-000496JASPER31C1', 'id': (497, 496, ' 1')}

def test_parser_inl():
    participation_factor = parse_inl("./tests/scenario_1/case.inl")[496, ' 2']
    assert participation_factor == {'id': (496, ' 2'), 'alpha_g': 90.5}

def test_parser_rop():
    cost = parse_rop("./tests/scenario_1/case.rop")[494, ' 1']
    assert cost == {'cost_table': 219, 'label': 'Linear 219', 'n_points': 6, 'x': [-1.01, 59.12, 79.34, 99.56, 119.78, 141.01], 'y': [-15.7863, 924.0456, 1252.014, 1591.9122, 1943.538, 2325.2534], 'coefficients': [0.011122953624314263, 14.906318926489629, 0.11711791544219821]}

def test_parser_raw():
    data = parse_raw("./tests/scenario_1/case.raw")
    assert data["buses"][1]["vm"] == 1.0400857
    assert data["loads"][1]["pl"] == 21.885521 / 100

def test_main():
    network = GOC_IO.parse_data("./tests/scenario_1")
    assert network[1]["generators"][272, " 1"]["contingency"] == True

def test_references():
    network = GOC_IO.parse_data("./tests/scenario_1")
    references = GOC_IO.build_references(network)
    assert len(references["bus_generators"][277]) == 4

def test_write_solution_1(): 
    network = GOC_IO.parse_data("./tests/scenario_1")
    solution1 = GOC_IO.get_solution_1(network)
    solution2 = GOC_IO.get_solution_2(network)

    assert len(solution1.splitlines()) == 658
    assert len(solution2.splitlines()) == 480736
