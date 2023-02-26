"""
This is arguably the main module of the libary, allowing the user to
count and retrieve earthquakes from the USGS database based on the
filter they have created. There is also a nice Earthquake class to
represent an earthquake in a Pythonic manner.
"""
from contextlib import suppress
from typing import Union

from . import filt
from ._utils import _get_type_error


MIN_TIMEOUT = 0.01
MAX_TIMEOUT = 86400 # 1 day - will never happen anyways due to server timeout.
MIN_RETRY_COUNT = 0
MAX_RETRY_COUNT = 1_000_000_000_000_000 # Realistically not exceeding...


class Earthquake:
    """Holds earthquake data."""
    pass


def count(
    earthquake_filter: filt.EarthquakeFilter,
    timeout: Union[int, float, None] = None,
    retry_count: Union[int, None] = 0) -> int:
    """
    Counts the number of earthquakes which match a given filter by
    sending a request to the USGS Earthquake API.

    Parameters:
        `earthquake_filter` [EarthquakeFilter] -
        the filter to count earthquakes by.
        
        `timeout` [int/float/None] - the maximum number of seconds the
        request may last. Raises a TimeoutError if the timeout is reached.
        Range (when numeric): 0.01 <= timeout <= 86400
        Default: None (no timeout)

        `retry_count` [int/None] - the maximum number of retries in the case
        of failed requests. When None, requests are sent forever until
        successful, meaning use this with caution as it could cause
        the program to hang indefinitely and overwhelm the API by sending
        requests non-stop. When 0, no retries are performed.
        Range (when numeric): retries >= 0
        Default: 0

    Returns: an integer which represents the number of earthquakes
    found to match the given filter.
    """
    from . import _requests # Prevents a circular import.
    if not isinstance(earthquake_filter, filt.EarthquakeFilter):
        raise _get_type_error(
            "earthquake_filter", filt.EarthquakeFilter, earthquake_filter)
    if not (timeout is None or isinstance(timeout, (int, float))):
        raise _get_type_error("timeout", (int, float, None), timeout)
    if not (retry_count is None or isinstance(retry_count, int)):
        raise _get_type_error("retry_count", (int, None), retry_count)
    if timeout is not None:
        if timeout < MIN_TIMEOUT:
            raise ValueError(f"Timeout must not be less than {MIN_TIMEOUT}")
        if timeout > MAX_TIMEOUT:
            raise ValueError(f"Timeout must not be greater than {MAX_TIMEOUT}")
    if retry_count is not None and retry_count < MIN_RETRY_COUNT:
        raise ValueError(
            f"Retry count must not be less than {MIN_RETRY_COUNT}")
    
    retry_count = min(
        MAX_RETRY_COUNT if retry_count is None else retry_count,
        MAX_RETRY_COUNT)
    for _ in range(retry_count):
        with suppress(Exception):
            return _requests._count(earthquake_filter, timeout)
    # Last chance. If the last chance fails, an error will be raised.
    return _requests._count(earthquake_filter, timeout)
