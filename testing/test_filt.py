"""Tests the `filt` module in the library."""
import unittest
from datetime import datetime
import sys

sys.path.append(".")
from equake import filt


class TimeFilterTest(unittest.TestCase):
    """Tests the `TimeFilter` class."""

    def test_normal_init(self) -> None:
        start = datetime(2020, 5, 15, 20, 15, 10)
        end = datetime(2021, 3, 23, 12, 12, 12)
        updated = datetime(2022, 1, 1, 1, 1, 1)
        time_filter = filt.TimeFilter(start, end, updated)
        self.assertEqual(time_filter.start, start)
        self.assertEqual(time_filter.end, end)
        self.assertEqual(time_filter.updated, updated)


if __name__ == "__main__":
    unittest.main()
