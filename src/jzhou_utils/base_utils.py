import re
from typing import List, Set, Any
import pickle
import os

"""
    Directory help:
"""


def list_files_in_directory(path, extensions=None):
    """
    List files in a directory, optionally filtering by extensions.

    :param path: Directory to search
    :param extensions: None, a string like 'txt', or a list like ['txt', 'csv']
    :return: List of matching file paths
    :raises FileNotFoundError: If the directory does not exist
    """
    if not os.path.isdir(path):
        raise FileNotFoundError(f"Directory not found: {path}")

    if extensions:
        if isinstance(extensions, str):
            extensions = [extensions]
        extensions = tuple(ext.lower().lstrip(".") for ext in extensions)

    result = []
    for file in os.listdir(path):
        full_path = os.path.join(path, file)
        if os.path.isfile(full_path):
            if not extensions or file.lower().endswith(
                tuple(f".{ext}" for ext in extensions)
            ):
                result.append(file)

    return result


"""
    File saving:
"""


def save_obj_pickle(file_path: str, raw_data) -> None:
    """
    Saves raw_data to file_path via pickle
    """
    with open(file_path, "wb") as handle:
        pickle.dump(raw_data, handle)


def read_obj_pickle(file_path: str):
    """
    Loads data in file_path via pickle
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Pickle file not found: {file_path}")

    with open(file_path, "rb") as f:
        return pickle.load(f)


"""
    Python default types:
"""


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
