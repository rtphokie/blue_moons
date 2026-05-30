# Blue Moon Calculator

Calculates blue moons — the second full moon in a calendar month — using precise astronomical ephemeris data. Times are reported in the system's local timezone.

Created to support  https://www.wral.com/weather/blue-moon-may-2026/ 

## Requirements

- Python 3.11+
- [skyfield](https://rhodesmill.org/skyfield/) (ephemeris calculations)

On first run, skyfield downloads the JPL DE421 ephemeris (~17 MB) to `~/.skyfield/`. Subsequent runs use the cached file.

## Usage

### Command line

```
python blue_moons.py --year 2023
python blue_moons.py --range 2020 2030
python blue_moons.py --next
python blue_moons.py --previous
```

Flags can be combined:

```
python blue_moons.py --year 2023 --next --previous
```

### Example output

```
$ python blue_moons.py --range 2020 2030 --next --previous

2020–2030: 4 blue moons
  October 31, 2020  10:49 EDT
  August 30, 2023  21:35 EDT
  May 31, 2026  04:45 EDT
  December 31, 2028  12:48 EDT

Next blue moon:     May 31, 2026  04:45 EDT

Previous blue moon: August 30, 2023  21:35 EDT
```

### Library

```python
from blue_moons import (
    blue_moons_in_year,
    blue_moons_in_range,
    next_blue_moon,
    previous_blue_moon,
)

# All blue moons in a single year
blues = blue_moons_in_year(2028)

# All blue moons across a range of years
blues = blue_moons_in_range(2020, 2030)

# Next blue moon from now
upcoming = next_blue_moon()

# Most recent blue moon before now
last = previous_blue_moon()

# Pass an explicit datetime to anchor next/previous
from datetime import datetime, timezone
anchor = datetime(2024, 1, 1, tzinfo=timezone.utc)
upcoming = next_blue_moon(after=anchor)
last = previous_blue_moon(before=anchor)
```

All functions return `datetime` objects in local time.

## Notes

- **Blue moon definition used:** calendar blue moon — the second full moon in a single calendar month. This is distinct from the seasonal blue moon (third full moon in a season with four full moons).
- **Timezone sensitivity:** whether a full moon falls in a given month depends on local time. A full moon at 01:00 UTC on the 1st may be the last day of the prior month locally. Times are classified using the system's local timezone.
- **Ephemeris coverage:** DE421 covers 1900–2050. Queries outside that range will produce inaccurate results.

## Tests

```
pytest test_blue_moons.py -v
```
