#!/usr/bin/env python3
"""Main Functions to run."""
import sys
import datetime
import requests
from .utils.range_handlers import handle_ranges_days, handle_ranges
from .utils.weeks import find_current_week_nott, find_week1, parse_week1, \
    academic_year_notice
from .utils.parsers import get_program_value, fetch_timetable, \
    parse_response
from .cli import get_school_interactive, parse_arguments, output_filename, \
    THIS_WEEK

GUI_FLAG = False
try:
    from .gui import NottApp
    GUI_FLAG = True
except ModuleNotFoundError:
    pass


def main():
    """Main Function to interface with nott-your-timetable.

    If GUI dependencies are installed, it will launch the GUI. Otherwise, it
    will default to CLI.
    """
    if GUI_FLAG:
        return main_gui()

    print("PyGObject not installed, deafulting to CLI.", file=sys.stderr)
    print("Please install the gi module or install the gui extras.",
          file=sys.stderr)
    return main_cli()


def _fetch_timetable_cli(program_value: str) -> str | None:
    """Fetches the timetable, printing a readable error on failure.

    Returns
    -------
    str | None
        The HTML report, or None if the request failed
    """
    try:
        return fetch_timetable(program_value)
    except requests.Timeout:
        print("HTTP request taking too long, please check your internet "
              "connection", file=sys.stderr)
    except requests.HTTPError as err:
        print(f"The timetable server rejected the request ({err}). The "
              "program list may be outdated, please update "
              "nott-your-timetable.", file=sys.stderr)
    except requests.RequestException as err:
        print(f"Unable to fetch timetable: {err}", file=sys.stderr)
    return None


def main_cli(argv: list[str] | None = None):
    """CLI main function."""
    args = parse_arguments(argv)
    today = datetime.date.today()
    # "This week" and "today" can only be resolved once week 1 is known
    relative_week = args.today or args.weeks == THIS_WEEK

    # Getting all the day and week ranges
    try:
        days = [today.isoweekday()] if args.today \
            else handle_ranges_days(args.days)
        weeks = [] if relative_week else handle_ranges(args.weeks)
    except ValueError:
        print("Invalid Range, Please Check Inserted Value", file=sys.stderr)
        return 1

    output = output_filename(args.output, args.format)

    # Checking if ranges are valid
    if (days[0] < 1 or days[-1] > 7) or \
            (weeks and (weeks[0] < 1 or weeks[-1] > 52)):
        print("Invalid Range, Please Check Inserted Value", file=sys.stderr)
        return 1

    # Interactive mode
    if args.interactive:
        school, program = get_school_interactive()
    else:
        school, program = args.course

    # Getting the pogram values
    try:
        program_value = get_program_value(school, program)
    except ValueError:
        print("Invalid School or Program", file=sys.stderr)
        return 1

    response = _fetch_timetable_cli(program_value)
    if response is None:
        return 1

    week1 = args.week1 or parse_week1(response)
    if week1 is None:
        week1 = find_week1()
        print(f"Warning: Couldn't read week 1 from the timetable, assuming "
              f"{week1.isoformat()}. Use --week1 to override.",
              file=sys.stderr)

    notice = academic_year_notice(week1, today)
    if notice is not None:
        print(f"Warning: {notice}", file=sys.stderr)

    if relative_week:
        weeks = [find_current_week_nott(week1, today)]

    schedule_data = parse_response(response, days, weeks, week1)
    return schedule_data.export(args.format, output)


def main_gui():
    """GUI main function."""
    app = NottApp()
    return app.run()
