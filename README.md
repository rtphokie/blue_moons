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
  October 31, 2020  10:49 EDT  (micromoon)
  August 30, 2023  21:35 EDT  (supermoon)
  May 31, 2026  04:45 EDT  (micromoon)
  December 31, 2028  12:48 EDT

Next blue moon:     May 31, 2026  04:45 EDT  (micromoon)

Previous blue moon: August 30, 2023  21:35 EDT  (supermoon)
```

### Library

```python
from blue_moons import (
    blue_moons_in_year,
    blue_moons_in_range,
    next_blue_moon,
    previous_blue_moon,
    moon_distance_km,
    moon_label,
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

```python
# Check distance and supermoon/micromoon status for a blue moon
dt = next_blue_moon()
print(moon_distance_km(dt))   # e.g. 406135.2 (km)
print(moon_label(dt))         # 'supermoon', 'micromoon', or None
```

## Supermoons and Micromoons

The Moon's orbit is elliptical, so its distance from Earth varies by about 12% between closest approach (perigee, ~356,000–370,000 km) and farthest point (apogee, ~404,000–407,000 km). This affects the Moon's apparent size and brightness.

- **Supermoon** — a full moon that occurs near perigee, making it appear up to 14% larger and 30% brighter than a full moon near apogee. This calculator uses the Sky & Telescope / TimeandDate.com threshold: distance **≤ 360,000 km**.
- **Micromoon** — a full moon near apogee, appearing smaller and dimmer than average. Threshold: distance **≥ 405,500 km**.
- The average Earth-Moon distance is ~384,400 km.

### Blue supermoons and blue micromoons (2020–2030)

| Date (EDT) | Distance | Classification |
|---|---|---|
| October 31, 2020 | 406,167 km | Blue micromoon |
| August 30, 2023 | 357,341 km | Blue supermoon |
| May 31, 2026 | 406,135 km | Blue micromoon |
| December 31, 2028 | 377,604 km | — |

A blue supermoon — a second full moon in a month *and* an unusually close full moon — is rare, occurring roughly once per decade. The August 2023 blue supermoon was the closest full moon of 2023 at 357,341 km, well inside the 360,000 km supermoon threshold.

## Notes

- **Blue moon definition used:** calendar blue moon — the second full moon in a single calendar month. This is distinct from the seasonal blue moon (third full moon in a season with four full moons).
- **Timezone sensitivity:** whether a full moon falls in a given month depends on local time. A full moon at 01:00 UTC on the 1st may be the last day of the prior month locally. Times are classified using the system's local timezone.
- **Ephemeris coverage:** DE421 covers 1900–2050. Queries outside that range will produce inaccurate results.

## Tests

```
pytest test_blue_moons.py -v
```
