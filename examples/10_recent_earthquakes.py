"""Displays the 10 most recent earthquakes."""
from equake import filt, quake


earthquake_filter = filt.EarthquakeFilter()
earthquakes = quake.get(earthquake_filter)
sorted_earthquakes = sorted(
    earthquakes, key=lambda event: event.time, reverse=True)

for earthquake in sorted_earthquakes[:10]:
    print(earthquake)
    print()
