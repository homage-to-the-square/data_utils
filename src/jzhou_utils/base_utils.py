import re
from typing import List, Set, Any

def map_dicts_values_to_keys(dict1, dict2) -> dict:
    """
        creates a new dictionary, which maps from keys of dict1 to values of dict2,
            assuming that the values of dict1 are keys of dict2
    """
    return {k: dict2[v] for k, v in dict1.items() if v in dict2}

def is_decimal(string: str) -> bool:
    """
        Given a string, checks if it is a representation of a decimal and returns a boolean 
    """
    return bool(re.match(r"^-?\d+(\.\d+)?$", string))

def intersect_sets(sets: List[Set[Any]]) -> Set[Any]:
    """
    Compute the intersection of a list of sets.

    Args:
        sets (List[Set[Any]]): A list of set objects.

    Returns:
        Set[Any]: The intersection of all sets in the list.
    """
    if not sets:
        return set()
    
    return set.intersection(*sets)