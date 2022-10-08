import csv

def parse_inl(filename: str) -> dict:
    """Read a unit inertia and governor response data file
    See section C.11 (eq. 173) for further details.

    Args:
        filename (str): path of the unit inertia and governor response file (*.inl)

    Returns:
        dict: mapping from `g` to `alpha_g`
    """
    if not filename.endswith(".inl"):
        raise NameError("Invalid filename, `parse_inl` works with *.inl files")

    participation_factor = {}
    with open(filename) as f:
        inl_reader = csv.reader(f)
        for row in inl_reader:
            if len(row) == 7:
                g = (int(row[0]), row[1].strip().rjust(2, ' ')) 
                alpha_g = float(row[5]) 

                participation_factor[g] = {
                    "id": g,
                    "alpha_g": alpha_g
                }
    return participation_factor
