"""
This module contains utility functions for the rest of the library.
It is private and should not be imported by the user.
"""
from typing import Tuple


def _get_type_error(
    name: str, allowed_types: Tuple[type], bad_data) -> TypeError:
    # Generates a TypeError based on the name of the data,
    # the allowed data types, and the type of the erroneous data.
    allowed_types_string = ""
    allowed_types_count = len(allowed_types)
    for i, _type in enumerate(allowed_types):
        # None does not have __name__ for some reason.
        type_name = _type.__name__ if _type is not None else "None"
        allowed_types_string += f"'{type_name}'"
        if i == allowed_types_count - 2:
            # Penultimate allowed data type.
            allowed_types_string += " or "
        if i < allowed_types_count - 2:
            allowed_types_string += ", "
    bad_data_type_name = (
        type(bad_data).__name__ if bad_data is not None else "None")
    return TypeError(
        f"'{name}' must be of type {allowed_types_string}, "
        f"not '{bad_data_type_name}'")
