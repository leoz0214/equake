"""
This module handles the sending of requests to the USGS API to retrieve
the earthquake counts/data. It is private.
"""
import json
from typing import Callable, Union
from urllib import error, request

from . import filt
from .exceptions import RequestError, HTTPError


BASE_URL = "https://earthquake.usgs.gov/fdsnws/event/1"
COUNT_URL = f"{BASE_URL}/count"
GET_URL = f"{BASE_URL}/query"

# Realistic minima/maxima to feed to the API.
# Remove extreme data before sending the request.
MIN_DEPTH_KM = -100
MAX_DEPTH_KM = 9999
MIN_MAGNTIUDE = -5
MAX_MAGNITUDE = 12

MAX_RADIUS_KM = 99999
MAX_REPORTS = 999_999_999 # No way this will be exceeded.


def _get_query_string(
    _filt: filt.EarthquakeFilter, limit: Union[int, None] = None) -> str:
    # Returns the query string to use based on the filter and limit.
    params = {
        "format": "geojson",
        "starttime": _filt.time_filter.start.isoformat(),
        "endtime": _filt.time_filter.end.isoformat(),
        "updatedafter": _filt.time_filter.updated.isoformat(),
    }
    if isinstance(_filt.location_filter, filt.RectLocationFilter):
        params["minlatitude"] = _filt.location_filter.min_lat
        params["minlongitude"] = _filt.location_filter.min_long
        params["maxlatitude"] = _filt.location_filter.max_lat
        params["maxlongitude"] = _filt.location_filter.max_long
    else:
        params["latitude"] = _filt.location_filter.lat
        params["longitude"] = _filt.location_filter.long
        if isinstance(_filt.location_filter, filt.CircleLocationFilter):
            params["radius"] = _filt.location_filter.radius
        else:
            params["radiuskm"] = min(
                _filt.location_filter.radius_km, MAX_RADIUS_KM)
    if _filt.depth_filter.min_km != float("-inf"):
        params["mindepth"] = max(_filt.depth_filter.min_km, MIN_DEPTH_KM)
    if _filt.depth_filter.max_km != float("inf"):
        params["maxdepth"] = min(_filt.depth_filter.max_km, MAX_DEPTH_KM)
    if _filt.magnitude_filter.min != float("-inf"):
        params["minmag"] = max(_filt.magnitude_filter.min, MIN_MAGNTIUDE)
    if _filt.magnitude_filter.max != float("inf"):
        params["maxmag"] = min(_filt.magnitude_filter.max, MAX_MAGNITUDE)
    if _filt.intensity_filter.min != filt.MIN_INTENSITY:
        params["minmmi"] = _filt.intensity_filter.min
    if _filt.intensity_filter.max != filt.MAX_INTENSITY:
        params["maxmmi"] = _filt.intensity_filter.max
    if _filt.pager_level is not None:
        params["alertlevel"] = _filt.pager_level
    if _filt.min_reports:
        params["minfelt"] = _filt.min_reports
    if limit is not None:
        params["limit"] = limit
    return "?" + "&".join(f"{key}={value}" for key, value in params.items())


def _handle_errors(func: Callable) -> Callable:
    # Decorator to catch errors in requests.
    def wrap(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except error.HTTPError as e:
            raise HTTPError(e.reason)
        except error.URLError as e:
            raise RequestError(e.reason)
        except TimeoutError as e:
            raise TimeoutError("Request to the API timed out.")
    return wrap


@_handle_errors
def _count(
    _filt: filt.EarthquakeFilter,
    timeout: Union[int, float, None] = None) -> int:
    # Requests a count of the number of earthquakes matching a given filter.
    query_string = _get_query_string(_filt)
    response = request.urlopen(f"{COUNT_URL}{query_string}", timeout=timeout)
    return json.loads(response.read())["count"]
