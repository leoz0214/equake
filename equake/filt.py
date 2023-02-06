"""
This module handles the functionality of earthquake filtering,
which allows you to search for earthquakes that meet particular
criteria, such as the time started and magnitude.

In fact, earthquake searches must be done with a filter, as there
are way too many recorded earthquakes for them all to be retrieved.
"""
from datetime import datetime, timedelta
from typing import Union

from ._utils import _get_type_error


DEFAULT_START_END_TIME_DAYS_GAP = 30

MIN_LATITUDE = -90
MAX_LATITUDE = 90
# Allow the International Date Line to be crossed by rectangles.
MIN_LONGITUDE = -360
MAX_LONGITUDE = 360


class EarthquakeFilter:
    """
    This class is used as the earthquake filter, storing the
    settings for various data points.
    """

    def __init__(self) -> None:
        pass


class TimeFilter:
    """
    Allows earthquakes to be searched based the time of the event
    and the time the event was updated.
    """

    def __init__(
        self, start: Union[datetime, None] = None,
        end: Union[datetime, None] = None,
        updated: Union[datetime, None] = None) -> None:
        """
        Creates a new `TimeFilter` object.

        Parameters:
            `start` - the earliest time to check for events
            (default 30 days before the end time). Must
            be earlier than the end time.

            `end` - the latest time to check for events
            (default current time). Must be later than the start time.

            `updated` - the earliest time that events must have been updated
            (default start time).

            All parameters are datetime objects or None.
        
        Note: all times are in UTC. Please be careful with local times.
        """
        if end is None:
            self._end = datetime.utcnow()
        elif isinstance(end, datetime):
            self._end = end
        else:
            raise _get_type_error("end", (datetime, None), end)

        if start is None:
            try:
                self._start = self._end - timedelta(
                    days=DEFAULT_START_END_TIME_DAYS_GAP)
            except OverflowError:
                # Cannot make time earlier from the end.
                # Only happens if the end time is earlier than
                # 1st January 1 AD 00:00:00 + default time gap.
                # Just make the start equal to the end instead.
                self._start = self._end
        elif isinstance(start, datetime):
            self._set_start(start)
        else:
            raise _get_type_error("start", (datetime, None), start)
        
        if updated is None:
            self._updated = self._start
        elif isinstance(updated, datetime):
            self._updated = updated
        else:
            raise _get_type_error("updated", (datetime, None), updated)
    
    def _set_start(self, start: datetime) -> None:
        # Sets the internal start time, validating it too.
        if start > self._end:
            raise ValueError(
                "Start time must not be later than end time.")
        self._start = start
    
    def _set_end(self, end: datetime) -> None:
        # Sets the internal end time, validating it too.
        if end < self.start:
            raise ValueError(
                "End time must not be earlier than the start time.")
        self._end = end
    
    def __repr__(self) -> str:
        return (
            f"TimeFilter({repr(self.start)}, {repr(self.end)}, "
            f"{repr(self.updated)})")
    
    def __str__(self) -> str:
        return f"Start: {self.start}\nEnd: {self.end}\nUpdated: {self.updated}"
        
    @property
    def start(self) -> datetime:
        """Starting time to check from."""
        return self._start

    @property
    def end(self) -> datetime:
        """Latest time to check from."""
        return self._end
    
    @property
    def updated(self) -> datetime:
        """Minimum updated time."""
        return self._updated
    
    @start.setter
    def start(self, start: datetime) -> None:
        if isinstance(start, datetime):
            self._set_start(start)
        else:
            raise _get_type_error("start", datetime, start)
    
    @end.setter
    def end(self, end: datetime) -> None:
        if isinstance(end, datetime):
            self._set_end(end)
        else:
            raise _get_type_error("end", datetime, end)
    
    @updated.setter
    def updated(self, updated: datetime) -> None:
        if isinstance(updated, datetime):
            self._updated = updated
        else:
            raise _get_type_error("updated", datetime, updated)


class _LocationFilter:
    """Private base class for any location filter classes."""


class RectLocationFilter(_LocationFilter):
    """
    Allows earthquakes to be filtered based on a
    rectangular location area by latitude/longitude.
    """

    def __init__(
        self, min_lat: Union[int, float], min_long: Union[int, float],
        max_lat: Union[int, float], max_long: Union[int, float]) -> None:
        """
        Creates a new `RectLocationFilter` object.

        Parameters:
            `min_lat` - the minimum latitude to search from.
            Range: -90 <= minimum latitude < maximum latitude

            `min_long` - the minimum longitude to search from.
            Range: -360 <= minimum longitude < maximum longitude

            `max_lat` - the maximum latitude to search from.
            Range: minimum latitude < maximum latitude <= 90

            `max_long` - the maximum longitude to search from.
            Range: minimum longitude < maximum longitude <= 360
        
        Note:
            Usually, longitude ranges from -180 to 180. However, the range
            has been doubled to -360 to 360. This allows rectangles to
            cross the International Date Line as needed.

            For example, searching from longitude -200 and -100 would be
            the equivalent of searching from longitude 160 and 260. If
            -180 or 180 lies between the minimum and maximum longitudes,
            the date line is indeed crossed.
        """
        for position, value in (
            ("min_lat", min_lat),
            ("min_long", min_long),
            ("max_lat", max_lat),
            ("max_long", max_long)
        ):
            if isinstance(value, (int, float)):
                getattr(self, f"_set_{position}")(value)
            else:
                raise _get_type_error(position, (int, float), value)
    
    def _set_min_lat(self, min_lat: Union[int, float]) -> None:
        # Validates and sets the minimum latitude.
        if min_lat < MIN_LATITUDE:
            raise ValueError(
                f"Minimum latitude must not be lower than {MIN_LATITUDE}.")
        if min_lat > getattr(self, "_max_lat", float("inf")):
            raise ValueError(
                "Minimum latitude must be less than maximum latitude.")
        self._min_lat = min_lat
    
    def _set_max_lat(self, max_lat: Union[int, float]) -> None:
        # Validates and sets the maximum latitude.
        if max_lat > MAX_LATITUDE:
            raise ValueError(
                f"Maximum latitude must not be higher than {MAX_LATITUDE}.")
        if max_lat < getattr(self, "_min_lat", float("-inf")):
            raise ValueError(
                "Maximum latitude must be higher than minimum latitude.")
        self._max_lat = max_lat
    
    def _set_min_long(self, min_long: Union[int, float]) -> None:
        # Validates and sets the minimum longitude.
        if min_long < MIN_LONGITUDE:
            raise ValueError(
                f"Minimum longitude must not be lower than {MIN_LONGITUDE}.")
        if min_long > getattr(self, "_max_long", float("inf")):
            raise ValueError(
                "Minimum longitude must be less than maximum longitude.")
        self._min_long = min_long
    
    def _set_max_long(self, max_long: Union[int, float]) -> None:
        # Validates and sets the maximum longitude.
        if max_long > MAX_LONGITUDE:
            raise ValueError(
                f"Maximum longitude must not be higher than {MIN_LONGITUDE}.")
        if max_long < getattr(self, "_min_long", float("-inf")):
            raise ValueError(
                "Maximum longitude must be higher than minimum longitude.")
        self._max_long = max_long
    
    # TODO - Remove boilerplate above, Getters and setters.
