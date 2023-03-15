"""
Relationship between intensity and magnitude.
Intensity against magnitude.
Starts at (3, 1)

As expected, in general, as magnitude increases, intensity increases.

Note: matplotlib required for this example.
"""
from equake import filt, quake
from datetime import datetime
from matplotlib import pyplot as plt


earthquake_filter = filt.EarthquakeFilter(
    time_filter=filt.TimeFilter(start=datetime(1, 1, 1)),
    magnitude_filter=filt.MagnitudeFilter(min_mag=3),
    intensity_filter=filt.IntensityFilter(min_intensity=1)
)
earthquakes = quake.get(earthquake_filter, 250)

magnitudes = []
intensities = []
for event in earthquakes:
    magnitudes.append(event.magnitude)
    intensities.append(event.intensity)

plt.scatter(magnitudes, intensities)
plt.show()
