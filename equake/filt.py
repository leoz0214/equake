"""
This module handles the functionality of earthquake filtering,
which allows you to search for earthquakes that meet particular
criteria, such as the time started and magnitude.

In fact, earthquake searches must be done with a filter, as there
are way too many recorded earthquakes for them all to be retrieved.
"""
from datetime import datetime, timedelta
from typing import Callable, Union

from ._utils import _get_type_error


DEFAULT_START_END_TIME_DAYS_GAP = 30

MIN_LATITUDE = -90
MAX_LATITUDE = 90
MIN_LONGITUDE = -180
MAX_LONGITUDE = 180
# To allow rectangles to cross the date line.
RECT_MIN_LONGITUDE = MIN_LONGITUDE * 2
RECT_MAX_LONGITUDE = MAX_LONGITUDE * 2


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
        elif not isinstance(end, datetime):
            raise _get_type_error("end", (datetime, None), end)
        else:
            self._end = end

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
        elif not isinstance(start, datetime):
            raise _get_type_error("start", (datetime, None), start)
        else:
            self._set_start(start)
        
        if updated is None:
            self._updated = self._start
        elif not isinstance(updated, datetime):
            raise _get_type_error("updated", (datetime, None), updated)
        else:
            self._updated = updated
    
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
        if not isinstance(start, datetime):
            raise _get_type_error("start", datetime, start)
        self._set_start(start)
    
    @end.setter
    def end(self, end: datetime) -> None:
        if not isinstance(end, datetime):
            raise _get_type_error("end", datetime, end)
        self._set_end(end)
    
    @updated.setter
    def updated(self, updated: datetime) -> None:
        if not isinstance(updated, datetime):
            raise _get_type_error("updated", datetime, updated)
        self._updated = updated


class _LocationFilter:
    """Private base class for any location filter classes."""

    def _type_check(identifier: str) -> Callable:
        # Decorator to ensure entered lat/long is numeric.
        def decorator(func: Callable) -> Callable:
            def wrapper(
                self: _LocationFilter, value: Union[int, float]
            ) -> None:
                if not isinstance(value, (int, float)):
                    raise _get_type_error(identifier, (int, float), value)
                func(self, value)
            return wrapper
        return decorator


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
        for value, position, orient, bound, bound_limit in (
            (min_lat, "min_lat", "latitude", "min", MIN_LATITUDE),
            (min_long, "min_long", "longitude", "min", RECT_MIN_LONGITUDE),
            (max_lat, "max_lat", "latitude", "max", MAX_LATITUDE),
            (max_long, "max_long", "longitude", "max", RECT_MAX_LONGITUDE)
        ):
            if not isinstance(value, (int, float)):
                raise _get_type_error(position, (int, float), value)
            self._set_position(
                value, f"_{position}", orient, bound, bound_limit)
    
    def _set_position(
        self, value: Union[int, float], attribute: str,
        orient: str, bound: str, bound_limit: int) -> None:
        # Validates and sets either the min/max lat/long.
        # orient: longitude/latitude, bound: min/max
        if bound == "min":
            if value < bound_limit:
                raise ValueError(
                    f"Minimum {orient} must not be less than {bound_limit}")
            # Must ensure min is not greater than max. Get max to do so.
            _max = getattr(self, attribute.replace("min", "max"), float("inf"))
            if value > _max:
                raise ValueError(
                    f"Minimum {orient} must be less than maximum {orient}")
        else:
            if value > bound_limit:
                raise ValueError(
                    f"Maximum {orient} must not be greater than {bound_limit}")
            # Must ensure max is not less than min. Get min to do so.
            _min = getattr(
                self, attribute.replace("max", "min"), float("-inf"))
            if value < _min:
                raise ValueError(
                    f"Maximum {orient} must be greater than minimum {orient}")
        setattr(self, attribute, value)
    
    def __repr__(self) -> str:
        return "RectLocationFilter("\
            f"{repr(self.min_lat)}, {repr(self.min_long)}, "\
            f"{repr(self.max_lat)}, {repr(self.max_long)})"
    
    def __str__(self) -> str:
        return f"Minimum latitude: {self.min_lat}\n"\
            f"Minimum longitude: {self.min_long}\n"\
            f"Maximum latitude: {self.max_lat}\n"\
            f"Maximum longitude: {self.max_long}"
    
    @property
    def min_lat(self) -> Union[int, float]:
        """Minimum latitude to search from."""
        return self._min_lat
    
    @property
    def min_long(self) -> Union[int, float]:
        """Minimum longitude to search from."""
        return self._min_long
    
    @property
    def max_lat(self) -> Union[int, float]:
        """Maximum latitude to search from."""
        return self._max_lat
    
    @property
    def max_long(self) -> Union[int, float]:
        """Maximum longitude to search from."""
        return self._max_long
    
    @min_lat.setter
    @_LocationFilter._type_check("min_lat")
    def min_lat(self, min_lat: Union[int, float]) -> None:
        self._set_position(
            min_lat, "_min_lat", "latitude", "min", MIN_LATITUDE)
    
    @min_long.setter
    @_LocationFilter._type_check("min_long")
    def min_long(self, min_long: Union[int, float]) -> None:
        self._set_position(
            min_long, "_min_long", "longitude", "min", RECT_MIN_LONGITUDE)
    
    @max_lat.setter
    @_LocationFilter._type_check("max_lat")
    def max_lat(self, max_lat: Union[int, float]) -> None:
        self._set_position(
            max_lat, "_max_lat", "latitude", "max", MAX_LATITUDE)
    
    @max_long.setter
    @_LocationFilter._type_check("max_long")
    def max_long(self, max_long: Union[int, float]) -> None:
        self._set_position(
            max_long, "_max_long", "longitude", "max", RECT_MAX_LONGITUDE)
