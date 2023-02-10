"""
This module handles the functionality of earthquake filtering,
which allows you to search for earthquakes that meet particular
criteria, such as the time started and magnitude.

In fact, earthquake searches must be done with a filter, as there
are way too many recorded earthquakes for them all to be retrieved.
"""
from datetime import datetime, timedelta
from typing import Callable, Union

from ._utils import _convert_units, _get_type_error, _method_type_check,


DEFAULT_START_END_TIME_DAYS_GAP = 30

MIN_LATITUDE = -90
MAX_LATITUDE = 90
MIN_LONGITUDE = -180
MAX_LONGITUDE = 180
# To allow rectangles to cross the date line.
RECT_MIN_LONGITUDE = MIN_LONGITUDE * 2
RECT_MAX_LONGITUDE = MAX_LONGITUDE * 2
# For the circle location filter class.
MIN_RADIUS = 0
MAX_RADIUS = 180
# Units.
KM = "km"
MI = "mi"
LENGTH_UNITS = {KM: 1, MI: 1.609344}


class EarthquakeFilter:
    """
    This class is used as the earthquake filter, storing the
    settings for various data points.
    """

    def __init__(self) -> None: #TODO once all sub-filters complete.
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
            raise ValueError("Start time must not be later than end time.")
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
        """Earliest updated time required."""
        return self._updated
    
    @start.setter
    @_method_type_check("start", datetime)
    def start(self, start: datetime) -> None:
        self._set_start(start)
    
    @end.setter
    @_method_type_check("end", datetime)
    def end(self, end: datetime) -> None:
        self._set_end(end)
    
    @updated.setter
    @_method_type_check("updated", datetime)
    def updated(self, updated: datetime) -> None:
        self._updated = updated


class _LocationFilter:
    """Private base class for any location filter classes."""

    def _type_check(identifier: str) -> Callable:
        # Validates that latitude/longitude is numeric.
        return _method_type_check(identifier, (int, float))


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

            All parameters must be integers or floats.
        Note:
            Usually, longitude ranges from -180 to 180. However, the range
            has been doubled to -360 to 360, allowing rectangles to
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


class _CircleLocationFilter(_LocationFilter):
    """
    Private base class for the location filters involving a
    circle and its radius.
    """

    def __init__(
        self, lat: Union[int, float], long: Union[int, float]
    ) -> None:
        for name, value in (("lat", lat), ("long", long)):
            if not isinstance(value, (int, float)):
                raise _get_type_error(name, (int, float), value)
        self._set_lat(lat)
        self._set_long(long)
    
    def _set_lat(self, lat: Union[int, float]) -> None:
        # Validates and sets the latitude.
        if lat < MIN_LATITUDE:
            raise ValueError(f"Latitude must not be less than {MIN_LATITUDE}")
        if lat > MAX_LATITUDE:
            raise ValueError(
                f"Latitude must not be greater than {MAX_LATITUDE}")
        self._lat = lat
    
    def _set_long(self, long: Union[int, float]) -> None:
        # Validates and sets the longitude.
        if long < MIN_LONGITUDE:
            raise ValueError(
                f"Longitude must not be less than {MIN_LONGITUDE}")
        if long > MAX_LONGITUDE:
            raise ValueError(
                f"Longitude must not be greater than {MAX_LONGITUDE}")
        self._long = long
    
    @property
    def lat(self) -> Union[int, float]:
        """Latitude of the point."""
        return self._lat
    
    @property
    def long(self) -> Union[int, float]:
        """Longitude of the point."""
        return self._long
    
    @lat.setter
    @_LocationFilter._type_check("lat")
    def lat(self, lat: Union[int, float]) -> None:
        self._set_lat(lat)
    
    @long.setter
    @_LocationFilter._type_check("long")
    def long(self, long: Union[int, float]) -> None:
        self._set_long(long)


class CircleLocationFilter(_CircleLocationFilter):
    """
    Allows earthquakes to be searched by the
    number of degrees within the radius of a point.
    """

    def __init__(
        self, lat: Union[int, float], long: Union[int, float],
        radius: Union[int, float]) -> None:
        """
        Creates a new `CircleLocationFilter` object.

        Parameters:
            `lat` - the latitude of the point.
            Range: -90 <= latitude <= 90

            `long`- the longitude of the point.
            Range: -180 <= longitude <= 180

            `radius` - the maximum number of degrees to search
            for from the point.
            Range: 0 <= radius <= 180

            All parameters must be integers or floats.
        """
        super().__init__(lat, long)
        if not isinstance(radius, (int, float)):
            raise _get_type_error("radius", (int, float), radius)
        self._set_radius(radius)
    
    def _set_radius(self, radius: Union[int, float]) -> None:
        # Validates and sets the radius.
        if radius < MIN_RADIUS:
            raise ValueError(f"Radius must not be less than {MIN_RADIUS}")
        if radius > MAX_RADIUS:
            raise ValueError(f"Radius must not be greater than {MAX_RADIUS}")
        self._radius = radius
    
    def __repr__(self) -> str:
        return f"CircleLocationFilter("\
            f"{repr(self.lat)}, {repr(self.long)}, {repr(self.radius)})"
    
    def __str__(self) -> str:
        return f"Latitude: {self.lat}\nLongitude: {self.long}\n"\
            f"Radius (degrees): {self.radius}"
    
    @property
    def radius(self) -> Union[int, float]:
        """Radius of the point in degrees."""
        return self._radius

    @radius.setter
    @_method_type_check("radius", (int, float))
    def radius(self, radius: Union[int, float]) -> None:
        self._set_radius(radius)


class CircleDistanceLocationFilter(_CircleLocationFilter):
    """
    Allows earthquakes to be searched within
    a given distance from a point.
    """

    def __init__(
        self, lat: Union[int, float], long: Union[int, float],
        radius: Union[int, float], radius_unit: str = KM) -> None:
        """
        Creates a new `CircleDistanceLocationFilter` object.

        Parameters:
            `lat` [int/float] - the latitude of the point.
            Range: -90 <= latitude <= 90

            `long` [int/float] - the longitude of the point.
            Range: -180 <= longitude <= 180

            `radius` [int/float] - the maximum distance from the point
            to search for earthquakes.
            Range: radius >= 0

            `radius_unit` [str['km'/'mi']] - the unit which the radius
            is in, either kilometres ('km') or miles ('mi'). Default: 'km'
        """
        super().__init__(lat, long)
        # Allow for leading/trailing whitespace.
        if not isinstance(radius_unit, str):
            raise _get_type_error("radius_unit", str, radius_unit)
        radius_unit = radius_unit.strip() 
        if radius_unit == MI:
            radius = _convert_units(radius, MI, KM, LENGTH_UNITS)
        elif radius_unit != KM:
            raise ValueError(
                f"Radius unit must be '{KM}' or '{MI}', not {radius_unit}")
        self._set_radius(radius)
    
    def _set_radius(self, radius: Union[int, float]) -> None:
        # Validates and sets the radius (km).
        if radius < MIN_RADIUS:
            raise ValueError(f"Radius must not be less than {MIN_RADIUS}")
        self._radius = radius
    
    def __repr__(self) -> str:
        return f"CircleDistanceLocationFilter("\
            f"{repr(self.lat)}, {repr(self.long)}, "\
            f"{repr(self.radius_km)}, '{KM}')"
    
    def __str__(self) -> str:
        return f"Latitude {self.lat}\nLongitude: {self.long}\n"\
            f"Radius (km): {self.radius_km}\nRadius (mi): {self.radius_mi}"
    
    @property
    def radius_km(self) -> Union[int, float]:
        """Radius of the point in kilometres."""
        return self._radius
    
    @property
    def radius_mi(self) -> Union[int, float]:
        """Radius of the point in miles."""
        return _convert_units(self.radius_km, KM, MI, LENGTH_UNITS)
    
    @radius_km.setter
    @_method_type_check("radius_km", (int, float))
    def radius_km(self, radius_km: Union[int, float]) -> None:
        return self._set_radius(radius_km)
    
    @radius_mi.setter
    @_method_type_check("radius_mi", (int, float))
    def radius_mi(self, radius_mi: Union[int, float]) -> None:
        return self._set_radius(
            _convert_units(radius_mi, MI, KM, LENGTH_UNITS))
