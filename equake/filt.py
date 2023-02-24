"""
This module handles the functionality of earthquake filtering,
which allows you to search for earthquakes that meet particular
criteria, such as the time and magnitude.

In fact, earthquake searches must be done with a filter, as there
are way too many recorded earthquakes for them all to be retrieved.
"""
from datetime import datetime, timedelta
from typing import Callable, Union

from ._utils import _convert_units, _get_type_error, _method_type_check


# Default start time and end time difference.
DEFAULT_DAYS_GAP = 30
# Earth co-ordinate constants.
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
# For the intensity filter class.
MIN_INTENSITY = 0
MAX_INTENSITY = 12
# For the master earthquake filter class.
MIN_REPORTS = 0
# Pager: Earthquake severity impact scale.
GREEN = "green"
YELLOW = "yellow"
ORANGE = "orange"
RED = "red"
PAGER_LEVELS = (GREEN, YELLOW, ORANGE, RED)
# Units.
KM = "km"
MI = "mi"
DISTANCE_UNITS = {KM: 1, MI: 1.609344}


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
        times = {"end": end, "start": start, "updated": updated}
        for name, _time in times.items(): # Order matters.
            if _time is None:
                if name == "end": # First
                    self.end = datetime.utcnow()
                if name == "start": # Second
                    try:
                        self.start = self.end - timedelta(DEFAULT_DAYS_GAP)
                    except OverflowError:
                        # Cannot make time any earlier from the end.
                        # Only happens if the end time is earlier than
                        # 1st January 1 AD 00:00:00 + default time gap.
                        # Just make the start equal to the end instead.
                        self.start = self.end
                if name == "updated": # Third
                    self.updated = self.start
            elif not isinstance(_time, datetime): # Not a datetime nor None.
                raise _get_type_error(name, (datetime, None), _time)
            else: # Just set the time via the corresponding setter.
                setattr(self, name, _time)
    
    def __repr__(self) -> str:
        return f"TimeFilter({repr(self.start)}, {repr(self.end)}, "\
            f"{repr(self.updated)})"
    
    def __str__(self) -> str:
        return f"Start: {self.start}\nEnd: {self.end}\nUpdated: {self.updated}"
        
    @property
    def start(self) -> datetime:
        """Earliest time to check from."""
        return self._start

    @property
    def end(self) -> datetime:
        """Latest time to check to."""
        return self._end
    
    @property
    def updated(self) -> datetime:
        """Earliest updated time required."""
        return self._updated
    
    @start.setter
    @_method_type_check("start", datetime)
    def start(self, start: datetime) -> None:
        if hasattr(self, "_end") and start > self.end:
            raise ValueError("Start time must not be later than end time.")
        self._start = start
    
    @end.setter
    @_method_type_check("end", datetime)
    def end(self, end: datetime) -> None:
        if hasattr(self, "_start") and end < self.start:
            raise ValueError("End time must not be earlier than start time.")
        self._end = end
    
    @updated.setter
    @_method_type_check("updated", datetime)
    def updated(self, updated: datetime) -> None:
        self._updated = updated


class _LocationFilter:
    """Private base class for any location filter classes."""

    @staticmethod
    def _lat_long_check(identifier: str) -> Callable:
        # Decorator validating that latitude/longitude is numeric.
        return _method_type_check(identifier, (int, float))


class RectLocationFilter(_LocationFilter):
    """
    Allows earthquakes to be filtered based on a
    rectangular location area by latitude/longitude.
    """

    def __init__(
        self, min_lat: Union[int, float] = MIN_LATITUDE,
        min_long: Union[int, float] = MIN_LONGITUDE,
        max_lat: Union[int, float] = MAX_LATITUDE,
        max_long: Union[int, float] = MAX_LONGITUDE) -> None:
        """
        Creates a new `RectLocationFilter` object.

        Parameters:
            `min_lat` - the minimum latitude to search from.
            Range: -90 <= minimum latitude <= maximum latitude
            Default: -90

            `min_long` - the minimum longitude to search from.
            Range: -360 <= minimum longitude <= maximum longitude
            Default: -180

            `max_lat` - the maximum latitude to search from.
            Range: minimum latitude <= maximum latitude <= 90
            Default: 90

            `max_long` - the maximum longitude to search from.
            Range: minimum longitude <= maximum longitude <= 360
            Default: 180

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
        self.min_lat = min_lat
        self.min_long = min_long
        self.max_lat = max_lat
        self.max_long = max_long
    
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
        """Maximum latitude to search to."""
        return self._max_lat
    
    @property
    def max_long(self) -> Union[int, float]:
        """Maximum longitude to search to."""
        return self._max_long
    
    @min_lat.setter
    @_LocationFilter._lat_long_check("min_lat")
    def min_lat(self, min_lat: Union[int, float]) -> None:
        if min_lat < MIN_LATITUDE:
            raise ValueError(
                f"Minimum latitude must not be less than {MIN_LATITUDE}")
        if hasattr(self, "_max_lat") and min_lat > self.max_lat:
            raise ValueError(
                "Minimum latitude must not be greater than maximum latitude.")
        self._min_lat = min_lat
    
    @min_long.setter
    @_LocationFilter._lat_long_check("min_long")
    def min_long(self, min_long: Union[int, float]) -> None:
        if min_long < RECT_MIN_LONGITUDE:
            raise ValueError(
                "Minimum longitude must not be less than", RECT_MIN_LONGITUDE)
        if hasattr(self, "_max_long") and min_long > self.max_long:
            raise ValueError(
                "Minimum longitude must not be greater than maximum longitude."
            )
        self._min_long = min_long
    
    @max_lat.setter
    @_LocationFilter._lat_long_check("max_lat")
    def max_lat(self, max_lat: Union[int, float]) -> None:
        if max_lat > MAX_LATITUDE:
            raise ValueError(
                f"Maximum latitude must not be greater than {MAX_LATITUDE}")
        if hasattr(self, "_min_lat") and max_lat < self.min_lat:
            raise ValueError(
                "Maximum latitude must not be less than minimum latitude.")
        self._max_lat = max_lat
    
    @max_long.setter
    @_LocationFilter._lat_long_check("max_long")
    def max_long(self, max_long: Union[int, float]) -> None:
        if max_long > RECT_MAX_LONGITUDE:
            raise ValueError(
                "Maximum longitude must not be greater than",
                RECT_MAX_LONGITUDE)
        if hasattr(self, "_min_long") and max_long < self.min_long:
            raise ValueError(
                "Maximum longitude must not be less than minimum longitude")
        self._max_long = max_long


class _CircleLocationFilter(_LocationFilter):
    """Private base class for the circle location filters."""

    def __init__(
        self, lat: Union[int, float], long: Union[int, float]
    ) -> None:
        self.lat = lat
        self.long = long

    @property
    def lat(self) -> Union[int, float]:
        """Latitude of the point."""
        return self._lat
    
    @property
    def long(self) -> Union[int, float]:
        """Longitude of the point."""
        return self._long
    
    @lat.setter
    @_LocationFilter._lat_long_check("lat")
    def lat(self, lat: Union[int, float]) -> None:
        if lat < MIN_LATITUDE:
            raise ValueError(f"Latitude must not be less than {MIN_LATITUDE}")
        if lat > MAX_LATITUDE:
            raise ValueError("Latitude must not be greater than", MAX_LATITUDE)
        self._lat = lat
    
    @long.setter
    @_LocationFilter._lat_long_check("long")
    def long(self, long: Union[int, float]) -> None:
        if long < MIN_LONGITUDE:
            raise ValueError("Longitude must not be less than", MIN_LONGITUDE)
        if long > MAX_LONGITUDE:
            raise ValueError(
                f"Longitude must not be greater than {MAX_LONGITUDE}")
        self._long = long


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
        self.radius = radius

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
        if radius < MIN_RADIUS:
            raise ValueError(f"Radius must not be less than {MIN_RADIUS}")
        if radius > MAX_RADIUS:
            raise ValueError(f"Radius must not be greater than {MAX_RADIUS}")
        self._radius = radius


class CircleDistanceLocationFilter(_CircleLocationFilter):
    """Allows earthquakes to be found within a given distance from a point."""

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
        if radius_unit == KM:
            self.radius_km = radius
        elif radius_unit == MI:
            self.radius_mi = radius
        else:
            raise ValueError(f"Radius unit must be '{KM}' or '{MI}'")
    
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
        return _convert_units(self.radius_km, KM, MI, DISTANCE_UNITS)
    
    @radius_km.setter
    @_method_type_check("radius_km", (int, float))
    def radius_km(self, radius_km: Union[int, float]) -> None:
        if radius_km < MIN_RADIUS: # Min = 0, so unit irrelevant.
            raise ValueError(f"Radius must not be less than {MIN_RADIUS}")
        self._radius = radius_km
    
    @radius_mi.setter
    @_method_type_check("radius_mi", (int, float))
    def radius_mi(self, radius_mi: Union[int, float]) -> None:
        self.radius_km = _convert_units(radius_mi, MI, KM, DISTANCE_UNITS)


class _RangeFilter:
    """Private base class for range filters by a min/max value."""

    @staticmethod
    def _type_check(identifier: str) -> Callable:
        # Decorator to check an input value is numeric (int/float).
        return _method_type_check(identifier, (int, float))

    def __init__(
        self, _min: Union[int, float], _max: Union[int, float], name: str,
        actual_min: Union[int, float] = float("-inf"),
        actual_max: Union[int, float] = float("inf")
    ) -> None:
        self._actual_min = actual_min
        self._actual_max = actual_max
        self._name = name
        if not isinstance(_min, (int, float)):
            raise _get_type_error("_min", (int, float), _min)
        if not isinstance(_max, (int, float)):
            raise _get_type_error("_max", (int, float), _max)
        self._set_min(_min)
        self._set_max(_max)
    
    def _set_min(self, _min: Union[int, float]) -> None:
        if _min < self._actual_min:
            raise ValueError(
                f"{self._name.title()} must not be "
                f"less than {self._actual_min}")
        if hasattr(self, "_max") and _min > self._max:
            raise ValueError(
                f"Minimum {self._name} must not be "
                f"greater than the maximum {self._name}.")
        self._min = _min
    
    def _set_max(self, _max: Union[int, float]) -> None:
        if _max > self._actual_max:
            raise ValueError(
                f"{self._name.title()} must not be "
                f"greater than {self._actual_max}")
        if hasattr(self, "_min") and _max < self._min:
            raise ValueError(
                f"Maximum {self._name} must not be "
                f"less than minimum {self._name}.")
        self._max = _max


class DepthFilter(_RangeFilter):
    """Allows earthquakes to be searched by depth."""

    def __init__(
        self, min_depth: Union[int, float] = float("-inf"),
        max_depth: Union[int, float] = float("inf"), unit: str = KM) -> None:
        """
        Creates a new `DepthFilter` object.

        Parameters:
            `min_depth` [int/float] - the minimum depth to search from.
            Range: negative infinity <= minimum depth <= maximum depth
            Default: negative infinity (no minimum restriction)

            `max_depth` [int/float] - the maximum depth to search from.
            Range: minimum depth <= maximum depth <= positive infinity
            Default: positive infinity (no maximum restriction)

            `unit` [str['km'/'mi']] - the unit the depths are in, either
            kilometres ('km') or miles ('mi'). Default: 'km'
        
        Note: it may seem strange that depth can be recorded as negative,
        as that would imply the earthquake occurred above the surface.
        This can happen when the earthquake depth is very shallow.
        """
        # Initialise first, if miles, account for unit after.
        super().__init__(min_depth, max_depth, "depth")
        if not isinstance(unit, str):
            raise _get_type_error("unit", str, unit)
        unit = unit.strip()
        if unit == MI:
            # Temporarily set min to -inf so max (mi) can be set below min (km)
            self.min_mi = float("-inf")
            self.max_mi = max_depth
            self.min_mi = min_depth
        elif unit != KM:
            raise ValueError(f"Unit must be either '{KM}' or '{MI}'")
    
    def __repr__(self) -> str:
        _min = (
            repr(self.min_km) if self.min_km != float("-inf")
            else "float('-inf')")
        _max = (
            repr(self.max_km) if self.max_km != float("inf")
            else "float('inf')")
        return f"DepthFilter({_min}, {_max}, '{KM}')"
    
    def __str__(self) -> str:
        lines = []
        if self.min_km != float("-inf"):
            lines.append(f"Minimum depth: {self.min_km}km ({self.min_mi}mi)")
        else:
            lines.append("Minimum depth: No restriction")
        if self.max_km != float("inf"):
            lines.append(f"Maximum depth: {self.min_km}km ({self.min_mi}mi)")
        else:
            lines.append("Maximum depth: No restriction")
        return "\n".join(lines)
    
    @property
    def min_km(self) -> Union[int, float]:
        """Minimum depth to search from in kilometres."""
        return self._min
    
    @property
    def min_mi(self) -> Union[int, float]:
        """Minimum depth to search from in miles."""
        return _convert_units(self.min_km, KM, MI, DISTANCE_UNITS)
    
    @property
    def max_km(self) -> Union[int, float]:
        """Maximum depth to search to in kilometres."""
        return self._max
    
    @property
    def max_mi(self) -> Union[int, float]:
        """Maximum depth to search to in miles."""
        return _convert_units(self.max_km, KM, MI, DISTANCE_UNITS)
    
    @min_km.setter
    @_RangeFilter._type_check("min_km")
    def min_km(self, min_km: Union[int, float]) -> None:
        self._set_min(min_km)
    
    @min_mi.setter
    @_RangeFilter._type_check("min_mi")
    def min_mi(self, min_mi: Union[int, float]) -> None:
        self._set_min(_convert_units(min_mi, MI, KM, DISTANCE_UNITS))
    
    @max_km.setter
    @_RangeFilter._type_check("max_km")
    def max_km(self, max_km: Union[int, float]) -> None:
        self._set_max(max_km)
    
    @max_mi.setter
    @_RangeFilter._type_check("max_mi")
    def max_mi(self, max_mi: Union[int, float]) -> None:
        self._set_max(_convert_units(max_mi, MI, KM, DISTANCE_UNITS))


class MagnitudeFilter(_RangeFilter):
    """
    Allows earthquakes to be searched by magnitude.
    The scale used is the Richter Scale.
    """

    def __init__(
        self, min_mag: Union[int, float] = float("-inf"),
        max_mag: Union[int, float] = float("inf")) -> None:
        """
        Creates a new `MagnitudeFilter` object.

        Parameters:
            `min_mag` - the minimum magnitude to search from.
            Range: negative infinity <= minimum <= maximum
            Default: negative infinity (no minimum restriction)

            `max_mag` - the maximum magnitude to search from.
            Range: minimum <= maximum <= positive infinity
            Default: positive infinity (no maximum restriction)

            Both parameters are integers or floats.
        
        Note: as the Richter Scale is logarithmic, magnitude can
        indeed be negative, but earthquakes with negative
        magnitudes are extremely weak and insignificant.
        """
        super().__init__(min_mag, max_mag, "magnitude")
    
    def __repr__(self) -> str:
        _min = repr(self.min) if self.min != float("-inf") else "float('-inf')"
        _max = repr(self.max) if self.max != float("inf") else "float('inf')"
        return f"MagnitudeFilter({_min}, {_max})"
    
    def __str__(self) -> str:
        _min = "Minimum magnitude: " +\
            str(self.min if self.min != float("-inf") else 'No restriction')
        _max = "Maximum magnitude: " +\
            str(self.max if self.max != float("inf") else 'No restriction')
        return f"{_min}\n{_max}"
    
    @property
    def min(self) -> Union[int, float]:
        """Minimum magnitude to search from."""
        return self._min
    
    @property
    def max(self) -> Union[int, float]:
        """Maximum magnitude to search to."""
        return self._max
    
    @min.setter
    @_RangeFilter._type_check("min")
    def min(self, min_mag: Union[int, float]) -> None:
        return self._set_min(min_mag)
    
    @max.setter
    @_RangeFilter._type_check("max")
    def max(self, max_mag: Union[int, float]) -> None:
        return self._set_max(max_mag)
    

class IntensityFilter(_RangeFilter):
    """
    Allows earthquakes to be searched by maximum intensity.
    The scale used is the Modified Mercalli intensity scale (MMI).
    """

    def __init__(
        self, min_intensity: Union[int, float] = MIN_INTENSITY,
        max_intensity: Union[int, float] = MAX_INTENSITY) -> None:
        """
        Creates a new `IntensityFilter` object.

        Parameters:
            `min_intensity` - the minimum intensity to search from.
            Range: 0 <= minimum intensity <= maximum intensity
            Default: 0 (no minimum restriction)

            `max_intensity` - the maximum intensity to search from.
            Range: minimum intensity <= maximum intensity <= 12
            Default: 12 (no maximum restriction)

            Both parameters are integers or floats.
        
        Note: it is the maximum MMI of an earthquake as that is
        considered 'intensity'.
        Also, intensity is not to be confused with magnitude.
        For information on the Modified Mercalli intensity scale, see:
        https://en.wikipedia.org/wiki/Modified_Mercalli_intensity_scale
        """
        super().__init__(
            min_intensity, max_intensity, "intensity",
            MIN_INTENSITY, MAX_INTENSITY)
    
    @property
    def min(self) -> Union[int, float]:
        """Minimum intensity to search from."""
        return self._min

    @property
    def max(self) -> Union[int, float]:
        """Maximum intensity to search to."""
        return self._max
    
    def __repr__(self) -> str:
        return f"IntensityFilter({repr(self.min)}, {repr(self.max)})"
    
    def __str__(self) -> str:
        return f"Minimum intensity: {self.min}\nMaximum intensity: {self.max}"
    
    @min.setter
    @_RangeFilter._type_check("min")
    def min(self, min_intensity: Union[int, float]) -> None:
        self._set_min(min_intensity)
    
    @max.setter
    @_RangeFilter._type_check("max")
    def max(self, max_intensity: Union[int, float]) -> None:
        self._set_max(max_intensity)


class EarthquakeFilter:
    """
    This class is used as the earthquake filter, storing the
    settings for various data points.
    """

    def __init__(
        self, time_filter: Union[TimeFilter, None] = None,
        location_filter: Union[_LocationFilter, None] = None,
        depth_filter: Union[DepthFilter, None] = None,
        magnitude_filter: Union[MagnitudeFilter, None] = None,
        intensity_filter: Union[IntensityFilter, None] = None,
        pager_level: Union[str, None] = None, min_reports: int = 0) -> None:
        """
        Creates a new `EarthquakeFilter` object.

        Parameters:
            `time_filter` [TimeFilter/None] - allows earthquakes to
            be filtered based on time. When None, this corresponds
            to a time filter with all default arguments: TimeFilter().
            This leads to recent earthquakes being obtained.
            Default: None

            `location_filter` [RectLocationFilter/CircleLocationFilter
            /CircleDistanceLocationFilter/None] - allows earthquakes to
            be filtered based on location. When None, location is irrelevant.
            A RectLocationFilter is created, spanning the entire Earth.
            Defeault: None

            `depth_filter` [DepthFilter/None] - allows earthquakes to be
            filtered based on depth. When None, depth is irrelevant.
            A DepthFilter is created with no depth restriction.
            Default: None

            `magnitude_filter` [MagnitudeFilter/None] - allows earthquakes to
            be filtered based on magnitude. When None, magnitude is irrelevant.
            A MagnitudeFilter is created with no magnitude restriction.
            Default: None

            `intensity_filter` [IntensityFilter/None] - allows earthquakes to
            be filtered based on intensity. When None, intensity is irrelevant.
            An IntensityFilter is created with no intensity restriction.
            Default: None

            `pager_level` [str['green'/'yellow'/'orange'/'red']/None] - allows
            earthquakes to be filtered based on a particular PAGER level.
            The PAGER impact scale highlights the severity of the damage an
            earthquake causes.
            Valid PAGER levels: green, yellow, orange, red
            Impact severity: green (little to none), yellow (slight),
            orange (moderate), red (severe).
            When None, the PAGER level is irrelevant.
            Default: None

            `min_reports` [int] - allows earthquakes to be filtered based on
            the minimum number of reports from the public.
            Range: minimum reports >= 0
            Default: 0
        """
        sub_filters = (
            ("time_filter", time_filter, (TimeFilter,)),
            ("location_filter", location_filter, (RectLocationFilter,
                CircleLocationFilter, CircleDistanceLocationFilter)),
            ("depth_filter", depth_filter, (DepthFilter,)),
            ("magnitude_filter", magnitude_filter, (MagnitudeFilter,)),
            ("intensity_filter", intensity_filter, (IntensityFilter,)))
        # Note - setters used - type checks and other validation included.
        for name, value, classes in sub_filters:
            # Either set value if not None or default init of filter.
            # Index 0 for either the only filter or RectLocationFilter.
            setattr(self, name, classes[0]() if value is None else value)
        self.pager_level = pager_level
        self.min_reports = min_reports
    
    def __repr__(self) -> str:
        return f"EarthquakeFilter({repr(self.time_filter)}, "\
            f"{repr(self.location_filter)}, {repr(self.depth_filter)}, "\
            f"{repr(self.magnitude_filter)}, {repr(self.intensity_filter)}, "\
            f"{repr(self.pager_level)}, {self.min_reports})"
    
    def __str__(self) -> str:
        return "----- Earthquake Filter -----\n"\
            f"--- Time ---\n{self.time_filter}\n\n"\
            f"--- Location ---\n{self.location_filter}\n\n"\
            f"--- Depth ---\n{self.depth_filter}\n\n"\
            f"--- Magnitude ---\n{self.magnitude_filter}\n\n"\
            f"--- Intensity ---\n{self.intensity_filter}\n\n"\
            f"--- PAGER level ---\n{self.pager_level}\n\n"\
            f"--- Minimum reports ---\n{self.min_reports}"
    
    @property
    def time_filter(self) -> TimeFilter:
        """The time filter object."""
        return self._time_filter
    
    @property
    def location_filter(self) -> _LocationFilter:
        """The location filter object."""
        return self._location_filter
    
    @property
    def depth_filter(self) -> DepthFilter:
        """The depth filter object."""
        return self._depth_filter
    
    @property
    def magnitude_filter(self) -> MagnitudeFilter:
        """The magnitude filter object."""
        return self._magnitude_filter
    
    @property
    def intensity_filter(self) -> IntensityFilter:
        """The intensity filter object."""
        return self._intensity_filter
    
    @property
    def pager_level(self) -> Union[str, None]:
        """The PAGER level set."""
        return self._pager_level
    
    @property
    def min_reports(self) -> int:
        """Minimum number of reports from the public."""
        return self._min_reports
    
    @time_filter.setter
    @_method_type_check("time_filter", TimeFilter)
    def time_filter(self, time_filter: TimeFilter) -> None:
        self._time_filter = time_filter

    @location_filter.setter
    @_method_type_check("location_filter", (
        RectLocationFilter, CircleLocationFilter,
        CircleDistanceLocationFilter))
    def location_filter(self, location_filter: _LocationFilter) -> None:
        self._location_filter = location_filter
    
    @depth_filter.setter
    @_method_type_check("depth_filter", DepthFilter)
    def depth_filter(self, depth_filter: DepthFilter) -> None:
        self._depth_filter = depth_filter
    
    @magnitude_filter.setter
    @_method_type_check("magnitude_filter", MagnitudeFilter)
    def magnitude_filter(self, magnitude_filter: MagnitudeFilter) -> None:
        self._magnitude_filter = magnitude_filter
    
    @intensity_filter.setter
    @_method_type_check("intensity_filter", IntensityFilter)
    def intensity_filter(self, intensity_filter: IntensityFilter) -> None:
        self._intensity_filter = intensity_filter
    
    @pager_level.setter
    @_method_type_check("pager_level", (str, None))
    def pager_level(self, pager_level: Union[str, None]) -> None:
        if pager_level is None:
            self._pager_level = None
            return
        pager_level = pager_level.strip()
        if pager_level not in PAGER_LEVELS:
            raise ValueError(
                "PAGER level must be 'green', 'yellow', 'orange' or 'red'.")
        self._pager_level = pager_level
    
    @min_reports.setter
    @_method_type_check("min_reports", int)
    def min_reports(self, min_reports: int) -> None:
        if min_reports < MIN_REPORTS:
            raise ValueError(
                f"Minimum reports must not be less than {MIN_REPORTS}")
        self._min_reports = min_reports
