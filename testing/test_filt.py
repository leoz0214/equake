"""Tests the `filt` module in the library."""
import random
import sys
import unittest
from datetime import datetime, timedelta
from itertools import combinations

sys.path.append(".")
from equake import filt
from equake.filt import *


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


class LocationFilterTest(unittest.TestCase):
    """Unit tests for location filter classes."""

    def test_rect(self) -> None:
        """Tests the `RectLocationFilter` class."""
        for _ in range(10000):
            min_lat = random.uniform(-95, 95)
            min_long = random.uniform(-380, 380)
            max_lat = random.uniform(-95, 95)
            max_long = random.uniform(-380, 380)
            if (
                max_lat < min_lat or max_long < min_long or
                abs(min_lat) > 90 or abs(min_long) > 360 or
                abs(max_lat) > 90 or abs(max_long) > 360
            ):
                with self.assertRaises(ValueError):
                    filt.RectLocationFilter(
                        min_lat, min_long, max_lat, max_long)
                continue
            rect_filter = filt.RectLocationFilter(
                min_lat, min_long, max_lat, max_long)
            if random.random() < 0.05:
                rect_filter = eval("filt." + repr(rect_filter))
            self.assertEqual(rect_filter.min_lat, min_lat)
            self.assertEqual(rect_filter.min_long, min_long)
            self.assertEqual(rect_filter.max_lat, max_lat)
            self.assertEqual(rect_filter.max_long, max_long)
            for i in range(8):
                erroneous = random.random() < 0.02
                if erroneous:
                    for attr in ("min_lat", "min_long", "max_lat", "max_long"):
                        with self.assertRaises(TypeError):
                            setattr(rect_filter, attr, None)
                    continue
                if i % 4 == 0:
                    new = random.uniform(-95, 95)
                    if new > rect_filter.max_lat or abs(new) > 90:
                        with self.assertRaises(ValueError):
                            rect_filter.min_lat = new
                        continue
                    rect_filter.min_lat = new
                    self.assertEqual(rect_filter.min_lat, new)
                if i % 4 == 1:
                    new = random.uniform(-380, 380)
                    if new > rect_filter.max_long or abs(new) > 360:
                        with self.assertRaises(ValueError):
                            rect_filter.min_long = new
                        continue
                    rect_filter.min_long = new
                    self.assertEqual(rect_filter.min_long, new)
                if i % 4 == 2:
                    new = random.randint(-95, 95)
                    if new < rect_filter.min_lat or abs(new) > 90:
                        with self.assertRaises(ValueError):
                            rect_filter.max_lat = new
                        continue
                    rect_filter.max_lat = new
                    self.assertEqual(rect_filter.max_lat, new)
                if i % 4 == 3:
                    new = random.uniform(-380, 380)
                    if new < rect_filter.min_long or abs(new) > 360:
                        with self.assertRaises(ValueError):
                            rect_filter.max_long = new
                        continue
                    rect_filter.max_long = new
                    self.assertEqual(rect_filter.max_long, new)
        for i in range(1000):
            params = [0, 0, 1, 1]
            params[i % 4] = "".join(
                chr(random.randint(1, 1000))
                for _ in range(random.randint(0, 10)))
            with self.assertRaises(TypeError):
                filt.RectLocationFilter(*params)
    
    def test_circle(self) -> None:
        """Tests the `CircleLocationFilter` class."""
        for _ in range(10000):
            lat = random.uniform(-95, 95)
            long = random.uniform(-190, 190)
            radius = random.uniform(-5, 185)
            if abs(lat) > 90 or abs(long) > 180 or not 0 <= radius <= 180:
                with self.assertRaises(ValueError):
                    filt.CircleLocationFilter(lat, long, radius)
                continue
            if random.random() < 0.05:
                selected = random.randrange(3)
                if selected == 0:
                    lat = None
                if selected == 1:
                    long = None
                if selected == 2:
                    radius = None
                with self.assertRaises(TypeError):
                    filt.CircleDistanceLocationFilter(lat, long, radius)
                continue
            circle_filter = filt.CircleLocationFilter(lat, long, radius)
            if random.random() < 0.05:
                circle_filter = eval("filt." + repr(circle_filter))
            self.assertEqual(circle_filter.lat, lat)
            self.assertEqual(circle_filter.long, long)
            self.assertEqual(circle_filter.radius, radius)
            for i in range(6):
                erroneous = random.random() < 0.02
                if erroneous:
                    for attr in ("lat", "long", "radius"):
                        with self.assertRaises(TypeError):
                            setattr(circle_filter, attr, None)
                    continue
                if i % 3 == 0:
                    new = random.uniform(-95, 95)
                    if abs(new) > 90:
                        with self.assertRaises(ValueError):
                            circle_filter.lat = new
                        continue
                    circle_filter.lat = new
                    self.assertEqual(circle_filter.lat, new)
                if i % 3 == 1:
                    new = random.uniform(-190, 190)
                    if abs(new) > 180:
                        with self.assertRaises(ValueError):
                            circle_filter.long = new
                        continue
                    circle_filter.long = new
                    self.assertEqual(circle_filter.long, new)
                if i % 3 == 2:
                    new = random.uniform(-5, 185)
                    if not 0 <= new <= 180:
                        with self.assertRaises(ValueError):
                            circle_filter.radius = new
                        continue
                    circle_filter.radius = radius
                    self.assertEqual(circle_filter.radius, radius)
    
    def test_circle_distance(self) -> None:
        """Tests the `CircleDistanceLocationFilter` class."""
        for _ in range(10000):
            lat = random.uniform(-95, 95)
            long = random.uniform(-190, 190)
            radius = random.uniform(-5000, 100000)
            unit = random.choice(
                ("km", " km", "km  ", " km ", "mi", "mi ", "Invalid."))
            if (
                abs(lat) > 90 or abs(long) > 180 or radius < 0
                or unit.strip() not in ("km", "mi")
            ):
                with self.assertRaises(ValueError):
                    filt.CircleDistanceLocationFilter(
                        lat, long, radius, unit)
                continue
            if random.random() < 0.05:
                selected = random.randrange(4)
                if selected == 0:
                    lat = None
                if selected == 1:
                    long = None
                if selected == 2:
                    radius = None
                if selected == 3:
                    unit = None
                with self.assertRaises(TypeError):
                    filt.CircleDistanceLocationFilter(lat, long, radius, unit)
                continue
            if random.random() < 0.05:
                circle_filter = filt.CircleDistanceLocationFilter(
                    lat, long, radius)
                unit = "km"
            else:
                circle_filter = filt.CircleDistanceLocationFilter(
                    lat, long, radius, unit)
            if random.random() < 0.05:
                circle_filter = eval("filt." + repr(circle_filter))
            self.assertEqual(circle_filter.lat, lat)
            self.assertEqual(circle_filter.long, long)
            if unit.strip() == "km":
                self.assertAlmostEqual(circle_filter.radius_km, radius)
            else:
                self.assertAlmostEqual(circle_filter.radius_mi, radius)
            for i in range(6):
                erroneous = random.random() < 0.02
                if erroneous:
                    for attr in ("lat", "long", "radius_km", "radius_mi"):
                        with self.assertRaises(TypeError):
                            setattr(circle_filter, attr, None)
                    continue
                if i % 3 == 0:
                    new = random.uniform(-95, 95)
                    if abs(new) > 90:
                        with self.assertRaises(ValueError):
                            circle_filter.lat = new
                        continue
                    circle_filter.lat = new
                    self.assertEqual(circle_filter.lat, new)
                if i % 3 == 1:
                    new = random.uniform(-190, 190)
                    if abs(new) > 180:
                        with self.assertRaises(ValueError):
                            circle_filter.long = new
                        continue
                    circle_filter.long = new
                    self.assertEqual(circle_filter.long, new)
                if i % 3 == 2:
                    unit = random.choice(("km", "mi"))
                    radius = random.uniform(-1000, 100000)
                    if radius < 0:
                        with self.assertRaises(ValueError):
                            circle_filter.radius_km = radius
                        with self.assertRaises(ValueError):
                            circle_filter.radius_mi = radius
                        continue
                    if unit == "km":
                        circle_filter.radius_km = radius
                        self.assertAlmostEqual(circle_filter.radius_km, radius)
                    else:
                        circle_filter.radius_mi = radius
                        self.assertAlmostEqual(circle_filter.radius_mi, radius)


class RangeFilterTest(unittest.TestCase):
    """Unit tests for the range filter classes."""

    def test_depth(self) -> None:
        """Tests the `DepthFilter` class."""
        for _ in range(10000):
            lower = random.uniform(-10000, 10000)
            upper = random.uniform(-5000, 15000)
            unit = random.choice(("km", " km ", "km ", "mi", " mi ", "XXX"))
            if unit.strip() not in ("km", "mi"):
                with self.assertRaises(ValueError):
                    filt.DepthFilter(lower, upper, unit)
                continue
            if random.random() < 0.1:
                depth_filter = filt.DepthFilter(lower, unit=unit)
                upper = float("inf")
            elif random.random() < 0.1:
                depth_filter = filt.DepthFilter(max_depth=upper, unit=unit)
                lower = float("-inf")
            elif random.random() < 0.02:
                with self.assertRaises(TypeError):
                    filt.DepthFilter("This", "is erroneous!")
                continue
            elif upper < lower:
                with self.assertRaises(ValueError):
                    filt.DepthFilter(lower, upper, unit)
                continue
            else:
                depth_filter = filt.DepthFilter(lower, upper, unit)
            if random.random() < 0.05:
                depth_filter = eval("filt." + repr(depth_filter))
            if unit.strip() == "km":
                self.assertAlmostEqual(depth_filter.min_km, lower)
                self.assertAlmostEqual(depth_filter.max_km, upper)
            else:
                self.assertAlmostEqual(depth_filter.min_mi, lower)
                self.assertAlmostEqual(depth_filter.max_mi, upper)
            for i in range(4):
                if random.random() < 0.1:
                    for attr in ("min_km", "min_mi", "max_km", "max_mi"):
                        with self.assertRaises(TypeError):
                            setattr(depth_filter, attr, "Nonsense")
                elif i % 2 == 0:
                    new = random.uniform(-10000, 10000)
                    if new > depth_filter.max_mi:
                        with self.assertRaises(ValueError):
                            depth_filter.min_mi = new
                    elif new < depth_filter.max_km:
                        depth_filter.min_km = new
                        self.assertAlmostEqual(depth_filter.min_km, new)
                    else:
                        with self.assertRaises(ValueError):
                            depth_filter.min_km = new
                        depth_filter.min_mi = float("-inf")
                        self.assertEqual(depth_filter.min_mi, float("-inf"))
                else:
                    new = random.uniform(-5000, 15000)
                    if new < depth_filter.min_km:
                        with self.assertRaises(ValueError):
                            depth_filter.max_km = new
                    elif new > depth_filter.min_mi:
                        depth_filter.max_mi = new
                        self.assertAlmostEqual(depth_filter.max_mi, new)
                    else:
                        with self.assertRaises(ValueError):
                            depth_filter.max_mi = new
                        depth_filter.max_km = float("inf")
                        self.assertEqual(depth_filter.max_km, float("inf"))
    
    def test_magnitude(self) -> None:
        """Test the `MagnitudeFilter` class."""
        for _ in range(10000):
            lower = random.uniform(-2, 8)
            upper = random.uniform(0, 10)
            if random.random() < 0.1:
                mag_filter = filt.MagnitudeFilter(lower)
                upper = float("inf")
            elif random.random() < 0.1:
                mag_filter = filt.MagnitudeFilter(max_mag=upper)
                lower = float("-inf")
            elif random.random() < 0.02:
                with self.assertRaises(TypeError):
                    filt.MagnitudeFilter(filt, TypeError)
                continue
            elif upper < lower:
                with self.assertRaises(ValueError):
                    filt.MagnitudeFilter(lower, upper)
                continue
            else:
                mag_filter = filt.MagnitudeFilter(lower, upper)
            if random.random() < 0.05:
                mag_filter = eval("filt." + repr(mag_filter))
            self.assertEqual(mag_filter.min, lower)
            self.assertEqual(mag_filter.max, upper)
            for i in range(4):
                if random.random() < 0.1:
                    for attr in ("min", "max"):
                        with self.assertRaises(TypeError):
                            setattr(mag_filter, attr, None)
                elif i % 2 == 0:
                    new = random.uniform(-2, 8)
                    if new > mag_filter.max:
                        with self.assertRaises(ValueError):
                            mag_filter.min = new
                        continue
                    mag_filter.min = new
                    self.assertEqual(mag_filter.min, new)
                else:
                    new = random.uniform(0, 10)
                    if new < mag_filter.min:
                        with self.assertRaises(ValueError):
                            mag_filter.max = new
                        continue
                    mag_filter.max = new
                    self.assertEqual(mag_filter.max, new)

    def test_intensity(self) -> None:
        """Tests the `IntensityFilter` class."""
        for _ in range(10000):
            lower = random.uniform(-1, 12)
            upper = random.uniform(0, 13)
            if not 0 <= lower <= upper <= 12:  
                with self.assertRaises(ValueError):
                    filt.IntensityFilter(lower, upper)
                continue
            elif random.random() < 0.02:
                with self.assertRaises(TypeError):
                    filt.IntensityFilter("Cat", self)
                continue
            else:
                intensity_filter = filt.IntensityFilter(lower, upper)
            if random.random() < 0.05:
                intensity_filter = eval("filt." + repr(intensity_filter))
            self.assertEqual(intensity_filter.min, lower)
            self.assertEqual(intensity_filter.max, upper)
            for i in range(4):
                if random.random() < 0.1:
                    for attr in ("min", "max"):
                        with self.assertRaises(TypeError):
                            setattr(intensity_filter, attr, [5])
                elif i % 2 == 0:
                    new = random.uniform(-1, 12)
                    if new < 0 or new > intensity_filter.max:
                        with self.assertRaises(ValueError):
                            intensity_filter.min = new
                        continue
                    intensity_filter.min = new
                    self.assertEqual(intensity_filter.min, new)
                else:
                    new = random.uniform(0, 13)
                    if new > 12 or new < intensity_filter.min:
                        with self.assertRaises(ValueError):
                            intensity_filter.max = new
                        continue
                    intensity_filter.max = new
                    self.assertEqual(intensity_filter.max, new)


class EarthquakeFilterTest(unittest.TestCase):
    """Tests the `EarthquakeFilter` class."""

    def generate_time_filter(self) -> filt.TimeFilter:
        return filt.TimeFilter(
            datetime(
                random.randint(1, 2022), random.randint(1, 12),
                random.randint(1, 28)),
            datetime(
                random.randint(2023, 9999), random.randint(1, 12),
                random.randint(1, 28)),
            updated=datetime(
                random.randint(1, 2022), random.randint(1, 12),
                random.randint(1, 28)))
    
    def generate_location_filter(self) -> filt._LocationFilter:
        return random.choice((
            filt.RectLocationFilter(
                random.randint(-90, 0), random.randint(-180, 0),
                random.randint(1, 90), random.randint(1, 180)),
            filt.CircleLocationFilter(
                random.randint(-90, 90), random.randint(-180, 180),
                random.uniform(0, 180)),
            filt.CircleDistanceLocationFilter(
                random.randint(-90, 90), random.randint(-180, 180),
                random.uniform(0, 100000), random.choice(("km", "mi")))))
    
    def generate_depth_filter(self) -> filt.DepthFilter:
        return filt.DepthFilter(
            random.uniform(-1000, 0), random.uniform(1, 1000),
            random.choice(("km", "mi")))
    
    def generate_magnitude_filter(self) -> filt.MagnitudeFilter:
        return filt.MagnitudeFilter(
            random.uniform(-1000, 0), random.uniform(1, 1000))
    
    def generate_intensity_filter(self) -> filt.IntensityFilter:
        return filt.IntensityFilter(random.uniform(0, 6), random.uniform(6, 12))
    
    def generate_pager_level(self):
        return random.choice(
            ("green", " green", "yellow", "yellow ",
            "orange", " orange ", "red", " red   ", None))
    
    def generate_min_reports(self) -> int:
        return random.randint(0, 10000)

    def test_init(self) -> None:
        for _ in range(1000):
            time_filter = (
                self.generate_time_filter() if random.random() < 0.9 else None)
            location_filter = (
                self.generate_location_filter() if random.random() < 0.9
                else None)
            depth_filter = (
                self.generate_depth_filter() if random.random() < 0.9 else None)
            magnitude_filter = (
                self.generate_magnitude_filter() if random.random() < 0.9
                else None)
            intensity_filter = (
                self.generate_intensity_filter() if random.random() < 0.9
                else None)
            pager_level = self.generate_pager_level()
            min_reports = self.generate_min_reports()
            erroneous = False
            if random.random() < 0.01:
                time_filter = "Erroneous"
                erroneous = True
            if random.random() < 0.01:
                location_filter = filt
                erroneous = True
            if random.random() < 0.01:
                depth_filter = filt._LocationFilter()
                erroneous = True
            if random.random() < 0.01:
                magnitude_filter = 7.7
                erroneous = True
            if random.random() < 0.01:
                intensity_filter = TypeError
                erroneous = True
            if random.random() < 0.01:
                pager_level = True
                erroneous = True
            if random.random() < 0.01:
                min_reports = 3.14
                erroneous = True
            if erroneous:
                with self.assertRaises(TypeError):
                    filt.EarthquakeFilter(
                        time_filter, location_filter, depth_filter,
                        magnitude_filter, intensity_filter,
                        pager_level, min_reports)
                continue
            invalid = False
            if random.random() < 0.01:
                pager_level = "i n v a l ID"
                invalid = True
            if random.random() < 0.01:
                min_reports = -29489234
                invalid = True
            if invalid:
                with self.assertRaises(ValueError):
                    filt.EarthquakeFilter(
                        time_filter, location_filter, depth_filter,
                        magnitude_filter, intensity_filter,
                        pager_level, min_reports)
                continue
            earthquake_filter = filt.EarthquakeFilter(
                time_filter, location_filter, depth_filter, magnitude_filter,
                intensity_filter, pager_level, min_reports)
            if time_filter is None:
                self.assertEqual(
                    earthquake_filter.time_filter.start,
                    earthquake_filter.time_filter.updated)
            else:
                self.assertEqual(
                    time_filter.__dict__,
                    earthquake_filter.time_filter.__dict__)
            if location_filter is None:
                self.assertEqual(
                    earthquake_filter.location_filter.min_lat, -90)
                self.assertEqual(
                    earthquake_filter.location_filter.min_long, -180)
                self.assertEqual(
                    earthquake_filter.location_filter.max_lat, 90)
                self.assertEqual(
                    earthquake_filter.location_filter.max_long, 180)
            else:
                self.assertEqual(
                    location_filter.__dict__,
                    earthquake_filter.location_filter.__dict__)
            if depth_filter is None:
                self.assertEqual(
                    earthquake_filter.depth_filter.min_km, float("-inf"))
                self.assertEqual(
                    earthquake_filter.depth_filter.max_mi, float("inf"))
            else:
                self.assertEqual(
                    depth_filter.__dict__,
                    earthquake_filter.depth_filter.__dict__)
            if magnitude_filter is None:
                self.assertEqual(
                    earthquake_filter.magnitude_filter.min, float("-inf"))
                self.assertEqual(
                    earthquake_filter.magnitude_filter.max, float("inf"))
            else:
                self.assertEqual(
                    magnitude_filter.__dict__,
                    earthquake_filter.magnitude_filter.__dict__)
            if intensity_filter is None:
                self.assertEqual(
                    earthquake_filter.intensity_filter.min, 0)
                self.assertEqual(
                    earthquake_filter.intensity_filter.max, 12)
            else:
                self.assertEqual(
                    intensity_filter.__dict__,
                    earthquake_filter.intensity_filter.__dict__)
            self.assertEqual(
                pager_level.strip() if pager_level is not None else None,
                earthquake_filter.pager_level)
            self.assertEqual(min_reports, earthquake_filter.min_reports)
    
    def test_repr(self) -> None:
        import datetime
        for _ in range(100):
            earthquake_filter = filt.EarthquakeFilter(
                self.generate_time_filter(),
                self.generate_location_filter(),
                self.generate_depth_filter(),
                self.generate_magnitude_filter(),
                self.generate_intensity_filter(),
                self.generate_pager_level(),
                self.generate_min_reports())
            evaluated = eval(repr(earthquake_filter))
            self.assertEqual(
                earthquake_filter.time_filter.__dict__,
                evaluated.time_filter.__dict__)
            self.assertEqual(
                earthquake_filter.location_filter.__dict__,
                evaluated.location_filter.__dict__)
            self.assertEqual(
                earthquake_filter.depth_filter.__dict__,
                evaluated.depth_filter.__dict__)
            self.assertEqual(
                earthquake_filter.magnitude_filter.__dict__,
                evaluated.magnitude_filter.__dict__)
            self.assertEqual(
                earthquake_filter.intensity_filter.__dict__,
                evaluated.intensity_filter.__dict__)
            self.assertEqual(
                earthquake_filter.pager_level, evaluated.pager_level)
            self.assertEqual(
                earthquake_filter.min_reports, evaluated.min_reports)
    
    def test_setters(self) -> None:
        earthquake_filter = filt.EarthquakeFilter()
        for i in range(1000):
            erroneous = random.random() < 0.05
            if erroneous:
                for attr in (
                    "time_filter", "location_filter", "depth_filter",
                    "magnitude_filter", "intensity_filter", "pager_level",
                    "min_reports"
                ):
                    with self.assertRaises(TypeError):
                        setattr(earthquake_filter, attr, TypeError)
                continue
            if i % 7 == 0:
                new = self.generate_time_filter()
                earthquake_filter.time_filter = new
                self.assertEqual(
                    new.__dict__, earthquake_filter.time_filter.__dict__)
            if i % 7 == 1:
                new = self.generate_location_filter()
                earthquake_filter.location_filter = new
                self.assertEqual(
                    new.__dict__, earthquake_filter.location_filter.__dict__)
            if i % 7 == 2:
                new = self.generate_depth_filter()
                earthquake_filter.depth_filter = new
                self.assertEqual(
                    new.__dict__, earthquake_filter.depth_filter.__dict__)
            if i % 7 == 3:
                new = self.generate_magnitude_filter()
                earthquake_filter.magnitude_filter = new
                self.assertEqual(
                    new.__dict__, earthquake_filter.magnitude_filter.__dict__)
            if i % 7 == 4:
                new = self.generate_intensity_filter()
                earthquake_filter.intensity_filter = new
                self.assertEqual(
                    new.__dict__, earthquake_filter.intensity_filter.__dict__)
            if i % 7 == 5:
                if random.random() < 0.1:
                    with self.assertRaises(ValueError):
                        earthquake_filter.pager_level = "Cat"
                    continue
                new = self.generate_pager_level()
                earthquake_filter.pager_level = new
                self.assertEqual(
                    new.strip() if new is not None else None,
                    earthquake_filter.pager_level)
            if i % 7 == 6:
                if random.random() < 0.1:
                    with self.assertRaises(ValueError):
                        earthquake_filter.min_reports = (
                            -self.generate_min_reports())
                new = self.generate_min_reports()
                earthquake_filter.min_reports = new
                self.assertEqual(new, earthquake_filter.min_reports)


if __name__ == "__main__":
    unittest.main()
