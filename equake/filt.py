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
            raise _get_type_error("start", (datetime,), start)
    
    @end.setter
    def end(self, end: datetime) -> None:
        if isinstance(end, datetime):
            self._set_end(end)
        else:
            raise _get_type_error("end", (datetime,), end)
    
    @updated.setter
    def updated(self, updated: datetime) -> None:
        if isinstance(updated, datetime):
            self._updated = updated
        else:
            raise _get_type_error("updated", (datetime,), updated)
