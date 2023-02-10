"""Tests the private `_utils` module in the library."""
import random
import sys
import unittest

sys.path.append(".")
from equake import _utils


class UtilsTest(unittest.TestCase):
    """Tests the private `_utils` module."""

    def test_get_type_error(self) -> None:
        types = (float, int, str, bool, list, set, tuple, dict, None)
        for i in range(3000):
            name = "".join(
                chr(random.randint(1, 10000))
                for _ in range(random.randint(1, 25)))
            allowed_types = (
                random.sample(types, random.randint(1, len(types)))
                if i < 2500 else random.choice(types))
            bad_data_type = random.choice(types)
            error_message = str(
                _utils._get_type_error(
                    name, allowed_types,
                    bad_data_type() if bad_data_type is not None else None))
            message_name, remainder = error_message.split(" must be of type ")
            message_allowed_types, message_bad_type = remainder.split(", not ")
            self.assertEqual(f"'{name}'", message_name)
            self.assertTrue(
                all(
                    str(getattr(_type, "__name__", "None"))
                    in message_allowed_types for _type in (
                    allowed_types if not (
                        allowed_types is None or
                        isinstance(allowed_types, type))
                    else (allowed_types,))))
            self.assertEqual(
                f"'{str(getattr(bad_data_type, '__name__', 'None'))}'",
                message_bad_type)
    
    def test_convert_units(self) -> None:
        for _ in range(100):
            value = random.uniform(0, 1000000)
            units = ["".join(
                chr(random.randint(1, 1000000))
                for __ in range(random.randint(2, 100)))
                for _ in range(random.randint(2, 10))]
            units_dict = {
                unit: random.uniform(0.0000001, 10000000) for unit in units
            }
            new_value = _utils._convert_units(
                value, units[0], units[1], units_dict)
            self.assertEqual(
                new_value,
                value * (units_dict[units[0]] / units_dict[units[1]]))


if __name__ == "__main__":
    unittest.main()
