from datetime import datetime, timezone
import pytest
from blue_moons import (
    blue_moons_in_year,
    blue_moons_in_range,
    next_blue_moon,
    previous_blue_moon,
    _LOCAL_TZ,
)

# Known full moon moments in UTC; converted to local time for assertions
# because blue moon classification and display use the local calendar date.
_KNOWN_UTC = [
    datetime(2020, 10, 31, 14, 49, tzinfo=timezone.utc),
    datetime(2023,  8, 31,  1, 35, tzinfo=timezone.utc),
    datetime(2026,  5, 31,  8, 45, tzinfo=timezone.utc),
    datetime(2028, 12, 31, 16, 48, tzinfo=timezone.utc),
]
KNOWN_BLUE_MOONS = [dt.astimezone(_LOCAL_TZ) for dt in _KNOWN_UTC]


def _approx_equal(a: datetime, b: datetime, tolerance_minutes: int = 2) -> bool:
    """True if two datetimes are within tolerance_minutes of each other."""
    return abs((a - b).total_seconds()) <= tolerance_minutes * 60


class TestBlueMoonsInYear:
    def test_2023_has_one_blue_moon(self):
        blues = blue_moons_in_year(2023)
        assert len(blues) == 1

    def test_2023_blue_moon_is_in_august(self):
        blues = blue_moons_in_year(2023)
        assert blues[0].month == 8
        assert _approx_equal(blues[0], KNOWN_BLUE_MOONS[1])

    def test_2020_has_one_blue_moon(self):
        blues = blue_moons_in_year(2020)
        assert len(blues) == 1

    def test_2020_blue_moon_is_in_october(self):
        blues = blue_moons_in_year(2020)
        assert blues[0].month == 10
        assert _approx_equal(blues[0], KNOWN_BLUE_MOONS[0])

    def test_year_with_no_blue_moon(self):
        # 2021 and 2022 have no blue moons
        assert blue_moons_in_year(2021) == []
        assert blue_moons_in_year(2022) == []

    def test_returns_local_datetimes(self):
        blues = blue_moons_in_year(2023)
        assert blues[0].tzinfo == _LOCAL_TZ

    def test_2028_blue_moon_is_in_december(self):
        blues = blue_moons_in_year(2028)
        assert len(blues) == 1
        assert blues[0].month == 12


class TestBlueMoonsInRange:
    def test_2020_to_2030_has_four_blue_moons(self):
        blues = blue_moons_in_range(2020, 2030)
        assert len(blues) == 4

    def test_2020_to_2030_dates_match_known(self):
        blues = blue_moons_in_range(2020, 2030)
        for actual, expected in zip(blues, KNOWN_BLUE_MOONS):
            assert _approx_equal(actual, expected), f"{actual} not close to {expected}"

    def test_single_year_range_matches_in_year(self):
        assert len(blue_moons_in_range(2023, 2023)) == len(blue_moons_in_year(2023))

    def test_range_with_no_blue_moons(self):
        assert blue_moons_in_range(2021, 2022) == []

    def test_results_are_chronological(self):
        blues = blue_moons_in_range(2000, 2030)
        assert blues == sorted(blues)

    def test_inclusive_end_year(self):
        # 2028 has a blue moon — it should be included when end_year=2028
        blues_inclusive = blue_moons_in_range(2027, 2028)
        blues_exclusive = blue_moons_in_range(2027, 2027)
        assert len(blues_inclusive) == len(blues_exclusive) + 1


class TestNextBlueMoon:
    def test_next_from_just_before_known(self):
        # One day before the Aug 2023 blue moon → should return that blue moon
        just_before = KNOWN_BLUE_MOONS[1] - __import__("datetime").timedelta(days=1)
        result = next_blue_moon(just_before)
        assert _approx_equal(result, KNOWN_BLUE_MOONS[1])

    def test_next_from_just_after_known(self):
        # One day after Aug 2023 blue moon → next is May 2026
        just_after = KNOWN_BLUE_MOONS[1] + __import__("datetime").timedelta(days=1)
        result = next_blue_moon(just_after)
        assert _approx_equal(result, KNOWN_BLUE_MOONS[2])

    def test_next_is_in_the_future(self):
        now = datetime.now(_LOCAL_TZ)
        result = next_blue_moon(now)
        assert result > now

    def test_next_is_a_blue_moon(self):
        # Verify the returned date is actually in the blue moon list for its year
        result = next_blue_moon(KNOWN_BLUE_MOONS[0] - __import__("datetime").timedelta(days=1))
        year_blues = blue_moons_in_year(result.year)
        assert any(_approx_equal(result, b) for b in year_blues)

    def test_returns_local_datetime(self):
        result = next_blue_moon()
        assert result.tzinfo == _LOCAL_TZ

    def test_n2_returns_second_upcoming(self):
        anchor = KNOWN_BLUE_MOONS[0] - __import__("datetime").timedelta(days=1)
        first = next_blue_moon(anchor, n=1)
        second = next_blue_moon(anchor, n=2)
        assert _approx_equal(first, KNOWN_BLUE_MOONS[1])
        assert _approx_equal(second, KNOWN_BLUE_MOONS[2])

    def test_n2_is_after_n1(self):
        now = __import__("datetime").datetime.now(_LOCAL_TZ)
        assert next_blue_moon(now, n=2) > next_blue_moon(now, n=1)

    def test_n1_matches_default(self):
        anchor = KNOWN_BLUE_MOONS[0]
        assert next_blue_moon(anchor, n=1) == next_blue_moon(anchor)


class TestPreviousBlueMoon:
    def test_previous_from_just_after_known(self):
        # One day after Aug 2023 → previous is Aug 2023
        just_after = KNOWN_BLUE_MOONS[1] + __import__("datetime").timedelta(days=1)
        result = previous_blue_moon(just_after)
        assert _approx_equal(result, KNOWN_BLUE_MOONS[1])

    def test_previous_from_just_before_known(self):
        # One day before Aug 2023 → previous is Oct 2020
        just_before = KNOWN_BLUE_MOONS[1] - __import__("datetime").timedelta(days=1)
        result = previous_blue_moon(just_before)
        assert _approx_equal(result, KNOWN_BLUE_MOONS[0])

    def test_previous_is_in_the_past(self):
        now = datetime.now(_LOCAL_TZ)
        result = previous_blue_moon(now)
        assert result < now

    def test_previous_is_a_blue_moon(self):
        result = previous_blue_moon(KNOWN_BLUE_MOONS[3] + __import__("datetime").timedelta(days=1))
        year_blues = blue_moons_in_year(result.year)
        assert any(_approx_equal(result, b) for b in year_blues)

    def test_next_and_previous_are_different(self):
        now = datetime.now(_LOCAL_TZ)
        assert next_blue_moon(now) != previous_blue_moon(now)

    def test_previous_before_next(self):
        now = datetime.now(_LOCAL_TZ)
        assert previous_blue_moon(now) < next_blue_moon(now)

    def test_returns_local_datetime(self):
        result = previous_blue_moon()
        assert result.tzinfo == _LOCAL_TZ
