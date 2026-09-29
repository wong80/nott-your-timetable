"""Tests for week calculations."""
# pylint: disable=missing-function-docstring
import datetime
import pytest
from nott_your_timetable.utils.weeks import find_first_day, find_week1, \
    parse_week1, find_current_week_nott, academic_year_notice


def test_parse_week1_from_report(eee_report):
    assert parse_week1(eee_report) == datetime.date(2025, 9, 1)


@pytest.mark.parametrize("header, expected", [
    ("<b>Weeks: 1-52 (1 Sep 2025-30 Aug 2026)</td>",
     datetime.date(2025, 9, 1)),
    ("Weeks: 1-52 ( 7  Sep 2026-5 Sep 2027)", datetime.date(2026, 9, 7)),
    ("no header here", None),
    ("Weeks: 1-52 (31 Foo 2025-30 Aug 2026)", None),
])
def test_parse_week1(header, expected):
    assert parse_week1(header) == expected


@pytest.mark.parametrize("day, iso, expected", [
    (0, False, 1),       # Monday, Sep 2025 starts on a Monday
    (1, True, 1),        # ISO Monday
    (7, True, 7),        # ISO Sunday
    (6, False, 7),       # Sunday
    ("Wed", False, 3),
])
def test_find_first_day(day, iso, expected):
    assert find_first_day(day, 2025, 9, iso=iso) == expected


def test_find_first_day_invalid():
    with pytest.raises(ValueError):
        find_first_day("Funday", 2025, 9)


@pytest.mark.parametrize("today, expected", [
    (datetime.date(2025, 9, 1), datetime.date(2025, 9, 1)),
    (datetime.date(2026, 3, 15), datetime.date(2025, 9, 1)),
    (datetime.date(2026, 9, 29), datetime.date(2026, 9, 7)),
])
def test_find_week1_fallback(today, expected):
    assert find_week1(today) == expected


@pytest.mark.parametrize("today, expected", [
    (datetime.date(2025, 9, 1), 1),
    (datetime.date(2025, 9, 7), 1),
    (datetime.date(2025, 9, 8), 2),
    (datetime.date(2025, 9, 22), 4),
    (datetime.date(2025, 8, 31), 0),
])
def test_find_current_week(today, expected):
    week1 = datetime.date(2025, 9, 1)
    assert find_current_week_nott(week1, today) == expected


@pytest.mark.parametrize("today", [
    datetime.date(2025, 9, 1),      # First day of week 1
    datetime.date(2026, 3, 15),
    datetime.date(2026, 8, 30),     # Last day of week 52
])
def test_academic_year_notice_current(today):
    assert academic_year_notice(datetime.date(2025, 9, 1), today) is None


@pytest.mark.parametrize("today", [
    datetime.date(2026, 8, 31),
    datetime.date(2026, 9, 29),     # New year not published yet
    datetime.date(2025, 8, 31),
])
def test_academic_year_notice_outside(today):
    notice = academic_year_notice(datetime.date(2025, 9, 1), today)
    assert "1 Sep 2025 - 30 Aug 2026" in notice
