#!/usr/bin/env python3
"""Functions to do calendar related calculations."""
from calendar import Calendar
import datetime
import re
from .enums import DayOfWeek

# Matches the report header e.g. "Weeks: 1-52 (1 Sep 2025-30 Aug 2026)"
_WEEKS_HEADER = re.compile(
    r"Weeks:\s*[\d\s,\-]+\(\s*(\d{1,2}\s+[A-Za-z]{3}\s+\d{4})"
)


def find_first_day(day: int | str, year: int, month: int,
                   iso: bool = False) -> int:
    """Finds the first day of week of a given month and year.

    Parameters
    ----------
    day: int | str
        The day of week to find
    year: int
        The year of interest
    month: int
        The month of interest
    iso: bool
        Use the ISO the numbering system to use when specifying day of week
        Can be ignored when day is given as a string

    Returns
    -------
    int
        They date of the month in which the first day of week appeared
    """
    cal: Calendar = Calendar()
    weeks = cal.monthdayscalendar(year, month)

    if isinstance(day, int):
        day_index = day - 1 if iso else day
    elif isinstance(day, str):
        try:
            day_index = DayOfWeek[day.title()].value
        except KeyError as err:
            raise ValueError("Invalid Day of Week") from err
    else:
        raise TypeError("day must be an int or str")

    day_number = 1
    for week in weeks:
        if week[day_index] > 0:
            day_number = week[day_index]
            break

    return day_number


def find_week1(today: datetime.date | None = None) -> datetime.date:
    """Estimates week 1 of the academic year.

    This is a fallback heuristic (first Monday of September). Prefer
    ``parse_week1`` on the timetable response, which is authoritative.

    Parameters
    ----------
    today: datetime.date | None
        The reference date, defaults to today

    Returns
    -------
    datetime.date
        The date of the first Monday of September.
    """
    if today is None:
        today = datetime.date.today()
    year: int = today.year - 1 if today.month < 9 else today.year
    day: int = find_first_day(0, year, 9)

    return datetime.date(year, 9, day)


def parse_week1(response: str) -> datetime.date | None:
    """Extracts the start date of week 1 from a timetable report.

    The report header contains e.g. ``Weeks: 1-52 (1 Sep 2025-30 Aug 2026)``.
    This assumes the report was requested starting from week 1.

    Parameters
    ----------
    response: str
        The HTML of the timetable report

    Returns
    -------
    datetime.date | None
        The start of week 1, or None if the header can't be found
    """
    match = _WEEKS_HEADER.search(response)
    if match is None:
        return None
    try:
        return datetime.datetime.strptime(
            " ".join(match.group(1).split()), "%d %b %Y"
        ).date()
    except ValueError:
        return None


def find_current_week_nott(week1: datetime.date | None = None,
                           today: datetime.date | None = None) -> int:
    """Finds the week number.

    Parameters
    ----------
    week1: datetime.date | None
        The start of week 1, defaults to ``find_week1()``
    today: datetime.date | None
        The reference date, defaults to today

    Returns
    -------
    int
        The current week number.
    """
    if today is None:
        today = datetime.date.today()
    if week1 is None:
        week1 = find_week1(today)
    diff = today - week1
    return diff.days // 7 + 1


def academic_year_notice(week1: datetime.date,
                         today: datetime.date | None = None) -> str | None:
    """Warns when the timetable's academic year doesn't include today.

    This happens e.g. at the start of a new academic year before the
    university publishes the new timetable.

    Parameters
    ----------
    week1: datetime.date
        The start of week 1 of the timetable
    today: datetime.date | None
        The reference date, defaults to today

    Returns
    -------
    str | None
        The warning, or None if today is within the academic year
    """
    if 1 <= find_current_week_nott(week1, today) <= 52:
        return None

    end = week1 + datetime.timedelta(weeks=52, days=-1)
    return (f"This timetable is for the academic year {week1.day} "
            f"{week1:%b %Y} - {end.day} {end:%b %Y}, which doesn't include "
            "today. The new timetable may not be published yet.")
