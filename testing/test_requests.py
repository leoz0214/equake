"""Tests the private `_requests` module in the library."""
import random
import sys
import unittest
from datetime import datetime

sys.path.append(".")
from equake import filt, _requests


class RequestsTest(unittest.TestCase):
    """Tests the private `_requests` module."""

    def test_query_string(self) -> None:
        default = filt.EarthquakeFilter()
        partial = filt.EarthquakeFilter(
            location_filter=filt.CircleLocationFilter(32.32, 34.34, 90),
            magnitude_filter=filt.MagnitudeFilter(min_mag=7.5),
            pager_level="orange", min_reports=10)
        full = filt.EarthquakeFilter(
            filt.TimeFilter(
                datetime(2015, 6, 1), datetime(2015, 6, 30, 23, 59, 59),
                datetime(2020, 1, 1)),
            filt.CircleDistanceLocationFilter(45, 45, 100, "mi"),
            filt.DepthFilter(10, 50),
            filt.MagnitudeFilter(5, 7),
            filt.IntensityFilter(6, 10),
            pager_level="orange", min_reports=25)
        extreme = filt.EarthquakeFilter(
            filt.TimeFilter(
                datetime(1, 1, 1, 1, 1, 1), datetime(9999, 9, 9, 9, 9, 9),
                datetime(13, 12, 11, 10, 9, 8)),
            filt.CircleDistanceLocationFilter(90, 180, 238794.234, "mi"),
            filt.DepthFilter(922489, 9323342.324, "mi"),
            filt.MagnitudeFilter(50, 500),
            filt.IntensityFilter(6.66, 6.66),
            pager_level="red", min_reports=10**100
        )
        for _filter, params in (
            (default, {
                "format": "geojson",
                "starttime": default.time_filter.start.isoformat(),
                "endtime": default.time_filter.end.isoformat(),
                "updatedafter": default.time_filter.updated.isoformat(),
                "minlatitude": default.location_filter.min_lat,
                "minlongitude": default.location_filter.min_long,
                "maxlatitude": default.location_filter.max_lat,
                "maxlongitude": default.location_filter.max_long
            }),
            (partial, {
                "format": "geojson",
                "starttime": partial.time_filter.start.isoformat(),
                "endtime": partial.time_filter.end.isoformat(),
                "updatedafter": partial.time_filter.updated.isoformat(),
                "latitude": partial.location_filter.lat,
                "longitude": partial.location_filter.long,
                "radius": partial.location_filter.radius,
                "minmag": partial.magnitude_filter.min,
                "alertlevel": partial.pager_level,
                "minfelt": partial.min_reports
            }),
            (full, {
                "format": "geojson",
                "starttime": full.time_filter.start.isoformat(),
                "endtime": full.time_filter.end.isoformat(),
                "updatedafter": full.time_filter.updated.isoformat(),
                "latitude": full.location_filter.lat,
                "longitude": full.location_filter.long,
                "radiuskm": full.location_filter.radius_km,
                "mindepth": full.depth_filter.min_km,
                "maxdepth": full.depth_filter.max_km,
                "minmag": full.magnitude_filter.min,
                "maxmag": full.magnitude_filter.max,
                "minmmi": full.intensity_filter.min,
                "maxmmi": full.intensity_filter.max,
                "alertlevel": full.pager_level,
                "minfelt": full.min_reports
            }),
            (extreme, {
                "format": "geojson",
                "starttime": extreme.time_filter.start.isoformat(),
                "endtime": extreme.time_filter.end.isoformat(),
                "updatedafter": extreme.time_filter.updated.isoformat(),
                "latitude": extreme.location_filter.lat,
                "longitude": extreme.location_filter.long,
                "radiuskm": 99999,
                "mindepth": 9999,
                "maxdepth": 9999,
                "minmag": 12,
                "maxmag": 12,
                "minmmi": 6.66,
                "maxmmi": 6.66,
                "alertlevel": extreme.pager_level,
                "minfelt": 999_999_999
            })
        ):
            limit = random.randint(1, 21000)
            query_string = _requests._get_query_string(_filter, limit)
            self.assertEqual(query_string[0], "?")
            actual_params = query_string[1:].split("&")
            for param in (f"{key}={value}" for key, value in params.items()):
                self.assertIn(param, actual_params)
                actual_params.remove(param)
            self.assertEqual([f"limit={min(limit, 20000)}"], actual_params)


if __name__ == "__main__":
    unittest.main()
