"""
Trying to obtain the 1960 Great Chilean Earthquake with the greatest
magnitude ever recorded - 9.5

One very easy way to do so is to filter by magnitude.
"""
from equake import filt, quake
from datetime import datetime


earthquake_filter = filt.EarthquakeFilter(
    time_filter=filt.TimeFilter(start=datetime(1, 1, 1)),
    magnitude_filter=filt.MagnitudeFilter(min_mag=9)
)
earthquakes = quake.get(earthquake_filter)

print(max(earthquakes, key=lambda event: event.magnitude))
