"""
This is arguably the main module of the libary, allowing the user to
count and retrieve earthquakes from the USGS database based on the
filter they have created. There is also a nice Earthquake class to
represent earthquakes in a Pythonic manner.
"""
from contextlib import suppress
from datetime import datetime, timedelta
from typing import Union

from . import filt
from ._utils import _convert_units, _get_type_error


MIN_TIMEOUT = 0.01
MAX_TIMEOUT = 86400 # 1 day - will never happen anyways due to server timeout.
MIN_RETRY_COUNT = 0
MAX_RETRY_COUNT = 1_000_000_000_000_000 # Realistically not exceeding...


class Earthquake:
    """
    Holds earthquake data.
    
    Please do not initiate this class directly as an user.
    """
    
    @staticmethod
    def _from_api(geojson: dict) -> "Earthquake":
        # Private static method to create an Earthquake object from the API.
        info = geojson["properties"]
        coordinates = geojson["geometry"]["coordinates"]
        earthquake = Earthquake()
        earthquake._magnitude = info["mag"]
        earthquake._place = info["place"] 
        earthquake._time = (
            datetime(1970, 1, 1) + timedelta(milliseconds=info["time"]))
        earthquake._updated_time = (
            datetime(1970, 1, 1) + timedelta(milliseconds=info["updated"]))
        earthquake._url = info["url"]
        earthquake._reports = info["felt"] or 0 # Null/None gets turned into 0.
        earthquake._intensity = info["mmi"]
        earthquake._pager_level = info["alert"]
        earthquake._significance = info["sig"]
        earthquake._latitude = coordinates[1]
        earthquake._longitude = coordinates[0]
        earthquake._depth_km = coordinates[2]
        return earthquake
    
    def __str__(self) -> str:
        return f"Magnitude: {self.magnitude}\nPlace: {self.place}\n"\
            f"Latitude: {self.latitude}\nLongitude: {self.longitude}\n"\
            "Depth: "+ (
                f"{self.depth_km}km ({self.depth_mi}mi)\n"
                if self.has_depth else "None\n") +\
            f"Time: {self.time}\nUpdated time: {self.updated_time}\n"\
            f"Reports: {self.reports}\nIntensity: {self.intensity}\n"\
            f"PAGER level: {self.pager_level}\n"\
            f"Significance: {self.significance}\nURL: {self.url}"

    @property
    def magnitude(self) -> Union[int, float, None]:
        """Magnitude of the earthquake based on the Richter Scale."""
        return self._magnitude
    
    @property
    def place(self) -> Union[str, None]:
        """A textual description of the earthquake location."""
        return self._place
    
    @property
    def time(self) -> Union[datetime, None]:
        """The time of the earthquake event (UTC)."""
        return self._time
    
    @property
    def time_since_epoch(self) -> Union[int, float, None]:
        """Returns the timestamp of the event."""
        if not self.has_time:
            return None
        return (self.time - datetime(1970, 1, 1)).total_seconds()
    
    @property
    def updated_time(self) -> Union[datetime, None]:
        """The time at which the event was last updated (UTC)."""
        return self._updated_time
    
    @property
    def updated_time_since_epoch(self) -> Union[int, float, None]:
        """Returns the timestamp of the updated time."""
        if self.updated_time is None:
            return None
        return (self.updated_time - datetime(1970, 1, 1)).total_seconds()
    
    @property
    def url(self) -> Union[str, None]:
        """A link to the event on the USGS website."""
        return self._url
    
    @property
    def reports(self) -> Union[int, None]:
        """The number of people who felt and reported the event."""
        return self._reports
    
    @property
    def intensity(self) -> Union[int, None]:
        """
        The maximum intensity of the event, based on the Modified Mercalli
        Intensity Scale. Not to be confused with magnitude.
        """
        return self._intensity
    
    @property
    def pager_level(self) -> Union[str, None]:
        """
        The PAGER level highlights the severity of the damage.
        This data point is often unavailable.

        Green - Little/no damage
        Yellow - Some damage
        Orange - A lot of damage.
        Red - Severe damage.

        For more information, visit this link:
        https://earthquake.usgs.gov/data/pager/background.php
        """
        return self._pager_level
    
    @property
    def significance(self) -> Union[int, None]:
        """
        The greater this number, the more significant this event was.
        This number is provided by the API and considers several factors
        including magnitude, reports and cost.
        """
        return self._significance
    
    @property
    def latitude(self) -> Union[int, float, None]:
        """The latitude of the earthquake event."""
        return self._latitude
    
    @property
    def longitude(self) -> Union[int, float, None]:
        """The longitude of the earthquake event."""
        return self._longitude

    @property
    def depth_km(self) -> Union[int, float, None]:
        """The depth of the event in kilometres."""
        return self._depth_km
    
    @property
    def depth_mi(self) -> Union[int, float, None]:
        """The depth of the event in miles."""
        if self.depth_km is None:
            return None
        return _convert_units(
            self.depth_km, filt.KM, filt.MI, filt.DISTANCE_UNITS)
    
    @property
    def has_magnitude(self) -> bool:
        """The magnitude of the event is available."""
        return self.magnitude is not None
    
    @property
    def has_place(self) -> bool:
        """The place of the event is available."""
        return self.place is not None
    
    @property
    def has_time(self) -> bool:
        """The time of the event is available."""
        return self.time is not None
    
    @property
    def has_updated_time(self) -> bool:
        """The updated time of the event is available."""
        return self.updated_time is not None
    
    @property
    def has_url(self) -> bool:
        """The URL to the event is available."""
        return self.url is not None
    
    @property
    def has_reports(self) -> bool:
        """The number of reports is available."""
        return self.reports is not None
    
    @property
    def has_intensity(self) -> bool:
        """The maximum intensity of the event is available."""
        return self.intensity is not None
    
    @property
    def has_pager_level(self) -> bool:
        """The PAGER level of the event is available."""
        return self.pager_level is not None
    
    @property
    def has_latitude(self) -> bool:
        """The latitude of the event is available."""
        return self.latitude is not None
    
    @property
    def has_longitude(self) -> bool:
        """The longitude of the event is available."""
        return self.longitude is not None
    
    @property
    def has_depth(self) -> bool:
        """The depth of the event is available."""
        return self.depth_km is not None


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
    
    from . import _requests # Prevents a circular import.
    retry_count = min(
        MAX_RETRY_COUNT if retry_count is None else retry_count,
        MAX_RETRY_COUNT)
    for _ in range(retry_count):
        with suppress(Exception):
            return _requests._count(earthquake_filter, timeout)
    # Last chance. If the last chance fails, an error will be raised.
    return _requests._count(earthquake_filter, timeout)
