"""
Blue Moon Calculator

A blue moon is the second full moon in a calendar month.

Uses skyfield for accurate moon phase calculations.
Ephemeris data is downloaded on first run (~17 MB, de421.bsp covers 1900-2050).

created to support an article on blue moons for wral.com
"""

from datetime import datetime, timezone, timedelta
import argparse
import os

from skyfield import api, almanac

# ---------------------------------------------------------------------------
# Ephemeris / timezone setup
# ---------------------------------------------------------------------------

_LOADER = api.Loader(os.path.expanduser("~/.skyfield"))
_EPH = _LOADER("de421.bsp")  # covers 1900–2050, ~17 MB
_TS = api.load.timescale(builtin=True)
_LOCAL_TZ = datetime.now().astimezone().tzinfo

FULL_MOON = 2  # almanac.moon_phases index for full moon


# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------

def _full_moons_in_range(start: datetime, end: datetime) -> list[datetime]:
    """Return local-time datetimes of all full moons between start and end.

    start/end may be naive (treated as UTC) or timezone-aware.
    """
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)
    t0 = _TS.from_datetime(start)
    t1 = _TS.from_datetime(end)
    times, phases = almanac.find_discrete(t0, t1, almanac.moon_phases(_EPH))
    return [t.utc_datetime().astimezone(_LOCAL_TZ) for t, p in zip(times, phases) if p == FULL_MOON]


def _is_blue_moon(moons: list[datetime], idx: int) -> bool:
    """True if the moon at idx is the second full moon in its local calendar month."""
    if idx == 0:
        return False
    prev = moons[idx - 1]
    curr = moons[idx]
    return prev.year == curr.year and prev.month == curr.month


def _blue_moons_from_list(moons: list[datetime]) -> list[datetime]:
    return [m for i, m in enumerate(moons) if _is_blue_moon(moons, i)]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def blue_moons_in_year(year: int) -> list[datetime]:
    """Return all blue moons in the given local-calendar year."""
    # 1-day buffer so timezone shifts at Jan 1 don't drop edge-case full moons
    start = datetime(year, 1, 1) - timedelta(days=1)
    end = datetime(year + 1, 1, 1) + timedelta(days=1)
    moons = _full_moons_in_range(start, end)
    return [b for b in _blue_moons_from_list(moons) if b.year == year]


def blue_moons_in_range(start_year: int, end_year: int) -> list[datetime]:
    """Return all blue moons from start_year through end_year inclusive."""
    start = datetime(start_year, 1, 1) - timedelta(days=1)
    end = datetime(end_year + 1, 1, 1) + timedelta(days=1)
    moons = _full_moons_in_range(start, end)
    return [b for b in _blue_moons_from_list(moons) if start_year <= b.year <= end_year]


def next_blue_moon(after: datetime | None = None) -> datetime:
    """Return the next blue moon after the given datetime (default: now, local time)."""
    after = after or datetime.now(_LOCAL_TZ)
    # Start 35 days early so we capture the first full moon of the current month,
    # which is needed to correctly classify the second one as a blue moon.
    search_start = after - timedelta(days=35)
    search_end = datetime(after.year + 3, after.month + 1, 1, tzinfo=timezone.utc)
    moons = _full_moons_in_range(search_start, search_end)
    blues = _blue_moons_from_list(moons)
    future = [b for b in blues if b > after]
    if not future:
        raise ValueError("No blue moon found in the next 3 years — expand search range")
    return future[0]


def previous_blue_moon(before: datetime | None = None) -> datetime:
    """Return the most recent blue moon before the given datetime (default: now, local time)."""
    before = before or datetime.now(_LOCAL_TZ)
    start = datetime(max(1900, before.year - 3), before.month, 1)
    moons = _full_moons_in_range(start, before)
    blues = _blue_moons_from_list(moons)
    past = [b for b in blues if b < before]
    if not past:
        raise ValueError("No blue moon found in the previous 3 years — expand search range")
    return past[-1]


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def _fmt(dt: datetime) -> str:
    return dt.strftime("%B %-d, %Y  %H:%M %Z")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Blue Moon Calculator — find blue moons (second full moon in a month)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python blue_moons.py --year 2023
  python blue_moons.py --range 2020 2030
  python blue_moons.py --next
  python blue_moons.py --previous
  python blue_moons.py --next --previous
""",
    )
    p.add_argument("--year", type=int, metavar="YEAR",
                   help="Count blue moons in a single year")
    p.add_argument("--range", nargs=2, type=int, metavar=("START", "END"),
                   help="Count blue moons over a range of years")
    p.add_argument("--next", action="store_true",
                   help="Show the next blue moon from today")
    p.add_argument("--previous", action="store_true",
                   help="Show the previous blue moon before today")
    return p


def main():
    parser = _build_parser()
    args = parser.parse_args()

    if not any([args.year, args.range, args.next, args.previous]):
        parser.print_help()
        return

    if args.year:
        blues = blue_moons_in_year(args.year)
        count = len(blues)
        print(f"\n{args.year}: {count} blue moon{'s' if count != 1 else ''}")
        for b in blues:
            print(f"  {_fmt(b)}")

    if args.range:
        start, end = args.range
        blues = blue_moons_in_range(start, end)
        count = len(blues)
        print(f"\n{start}–{end}: {count} blue moon{'s' if count != 1 else ''}")
        for b in blues:
            print(f"  {_fmt(b)}")

    if args.next:
        b = next_blue_moon()
        print(f"\nNext blue moon:     {_fmt(b)}")

    if args.previous:
        b = previous_blue_moon()
        print(f"\nPrevious blue moon: {_fmt(b)}")


if __name__ == "__main__":
    main()
