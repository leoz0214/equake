# equake
`equake` is a Python library to intuitively access and handle earthquake data.

This library retrieves earthquake data from the **USGS earthquake database** and allows
you to apply various filters to customise your search.

## Benefits

- This library is a convenient wrapper of the USGS Earthquake API, meaning you
  can communicate with its key functionality in an object-oriented, Pythonic way.
- Plenty of very thorough **validation** is provided to ensure robustness.
- The **abstraction** means you can focus on the more important details of your
  program rather than actually preparing the query string to send a request, for example.
- Both **kilometres and miles** are supported.
- The code has been rigorously **tested** for Python 3.7 and above, and major bugs have been fixed.
- The library has been **documented** fully, with the documentation inside the code.
- There are **no third-party dependencies** at all, not even the widely used requests library.
  This makes installation of the library very easy and error-free.

## Installation

Pip can be used to easily install this library.

`pip install equake`

Note: This library supports **Python 3.7** and above. Slightly older versions might work, but
they have not been tested, so this is not guaranteed. Python 2 is incompatible.

## Getting Started

For full details, consult the code documentation.

The main modules available are `filt` and `quake`

`filt` handles the filter functionality, allowing you to create filters to search for earthquakes.

`quake` allows you to count/get earthquakes from the API, and also holds the Earthquake class.

### Create a Filter

To search for earthquakes, you first must create a filter in the `filt` module.

The overarching filter object is `EarthquakeFilter`, which consists of sub-filters.
- `TimeFilter` - filter earthquakes by **time** of the event, and time updated.
- `LocationFilter` - filter earthquakes by **location** (Rectangle/Circle).
- `DepthFilter` - filter earthquakes by **depth**.
- `MagnitudeFilter` - filter earthquakes by **magnitude**.
- `IntensityFilter` - filter earthquakes by **maximum intensity**.
- PAGER Level - filter earthquakes by **severity** of damage.
- Minimum reports - filter earthquakes by **minimum number of reports** from the public.

For example, to create a filter for earthquakes with a depth between 100 and 200 kilometres,
a magnitude between 5 and 7, a PAGER level of 'orange', and 100 minimum reports, the
following code would be used:

```
from equake import filt

earthquake_filter = filt.EarthquakeFilter(
    filt.DepthFilter(100, 200),
    filt.MagnitudeFilter(5, 7),
    pager_level="orange",
    min_reports=100
)
```

*For more complex use cases, see the examples folder and the documentation.*

### Count or Get Earthquakes

Once you have a filter, you can count/get earthquakes by using the `quake` module.

To count/get the number of earthquakes in a simple way, this is the code you would use.

```
from equake import filt, quake

earthquake_filter = filt.EarthquakeFilter() # Just for example purposes.
earthquake_count = quake.count(earthquake_filter)
earthquakes = quake.get(earthquake_filter)
```

*Again, for more complex use cases, see the examples folder and the documentation.*
