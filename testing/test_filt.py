"""Tests the `filt` module in the library."""
import random
import sys
import unittest
from datetime import datetime, timedelta
from itertools import combinations

sys.path.append(".")
from equake import filt


class TimeFilterTest(unittest.TestCase):
    """Tests the `TimeFilter` class."""

    def check_correct_init(
        self, start: datetime, end: datetime, updated: datetime) -> None:
        """
        Checks start, end and updated are the same
        once the TimeFilter object is created.
        """
        time_filter = filt.TimeFilter(start, end, updated)
        self.assertEqual(time_filter.start, start)
        self.assertEqual(time_filter.end, end)
        self.assertEqual(time_filter.updated, updated)
    
    def generate_erroneous_data(self) -> None:
        """Returns a simple object which is not a datetime object."""
        return random.choice((
            random.randint(-10**100, 10**100), random.random(),
            "".join(
                chr(random.randint(1, 10000))
                for _ in range(random.randint(0, 100))), []))
    
    def generate_random_time(self) -> datetime:
        """Generates a simple random time (days up to 28 for simplicity)."""
        return datetime(
            random.randint(1, 9999), random.randint(1, 12),
            random.randint(1, 28), random.randint(0, 23),
            random.randint(0, 59), random.randint(0, 59))

    def test_all_datetime_params_init(self) -> None:
        for i in range(11000):
            start = self.generate_random_time()
            end = datetime(
                # Also perform some tests guaranteeing the start
                # and end times being in the same year.
                random.randint(1, 9999) if i < 10000 else start.year,
                random.randint(1, 12),
                random.randint(1, 28), random.randint(0, 23),
                random.randint(0, 59), random.randint(0, 59))
            updated = self.generate_random_time()
            if start > end:
                with self.assertRaises(ValueError):
                    filt.TimeFilter(start, end, updated)
                continue
            self.check_correct_init(start, end, updated)
        for _ in range(100):
            start = end = updated = datetime.utcnow()
            self.check_correct_init(start, end, updated)
    
    def test_start_and_updated_none(self) -> None:
        for i in range(1100):
            end = self.generate_random_time() if i < 1000 else (
                datetime(
                    1, 1, random.randint(1, 29), random.randint(0, 23),
                    random.randint(0, 59), random.randint(0, 59)))
            time_filter = filt.TimeFilter(end=end)
            try:
                self.assertEqual(time_filter.start, end - timedelta(30))
            except OverflowError:
                self.assertEqual(time_filter.start, time_filter.end)
            self.assertEqual(time_filter.start, time_filter.updated)
    
    def test_end_none(self) -> None:
        for _ in range(1000):
            start = self.generate_random_time()
            updated = self.generate_random_time()
            current_time = datetime.utcnow()
            if start > current_time:
                with self.assertRaises(ValueError):
                    filt.TimeFilter(start, None, updated)
                continue
            time_filter = filt.TimeFilter(start, None, updated)
            self.assertGreaterEqual(time_filter.end, current_time)
            self.assertLess(
                time_filter.end, current_time + timedelta(seconds=1))
    
    def test_all_none(self) -> None:
        for _ in range(1000):
            current_time = datetime.utcnow()
            time_filter = filt.TimeFilter()
            self.assertGreaterEqual(time_filter.end, current_time)
            self.assertLess(
                time_filter.end, current_time + timedelta(seconds=1))
            # It's the 21st century, no need to worry about overflow etc.
            self.assertGreaterEqual(
                time_filter.start, current_time - timedelta(30))
            self.assertEqual(time_filter.start, time_filter.updated)
    
    def test_erroneous_input(self) -> None:
        for _ in range(100):
            for l in range(1, 4):
                for param_combo in combinations(
                    ("start", "end", "updated"), l
                ):
                    with self.assertRaises(TypeError):
                        filt.TimeFilter(
                            **{
                                param: self.generate_erroneous_data()
                                for param in param_combo
                            })
    
    def test_repr(self) -> None:
        # The datetime object includes the module name (datetime).
        import datetime
        for _ in range(100):
            time_filter = filt.TimeFilter()
            eval_time_filter = eval(f"filt.{repr(time_filter)}")
            self.assertEqual(time_filter.start, eval_time_filter.start)
            self.assertEqual(time_filter.end, eval_time_filter.end)
            self.assertEqual(time_filter.updated, eval_time_filter.updated)
    
    def test_setters(self) -> None:
        time_filter = filt.TimeFilter()
        for i in range(10000):
            test_erroneous = random.random() < 0.1
            if test_erroneous:
                erroneous_data = self.generate_erroneous_data()
                with self.assertRaises(TypeError):
                    if i % 3 == 0:
                        time_filter.start = erroneous_data
                    elif i % 3 == 1:
                        time_filter.end = erroneous_data
                    else:
                        time_filter.updated = erroneous_data
                continue
            if i % 3 == 0: # Test start
                new_start = self.generate_random_time()
                if new_start > time_filter.end:
                    with self.assertRaises(ValueError):
                        time_filter.start = new_start
                    continue
                time_filter.start = new_start
                self.assertEqual(time_filter.start, new_start)
            elif i % 3 == 1: # Test end
                new_end = self.generate_random_time()
                if new_end < time_filter.start:
                    with self.assertRaises(ValueError):
                        time_filter.end = new_end
                    continue
                time_filter.end = new_end
                self.assertEqual(time_filter.end, new_end)
            else: # Test updated
                new_updated = self.generate_random_time()
                time_filter.updated = new_updated
                self.assertEqual(time_filter.updated, new_updated)


if __name__ == "__main__":
    unittest.main()
