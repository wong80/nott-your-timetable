"""Tests for CLI helpers and argument parsing."""
# pylint: disable=missing-function-docstring
import datetime
import pytest
import requests
from nott_your_timetable import nott_your_timetable as app
from nott_your_timetable.cli import output_filename, parse_arguments, \
    THIS_WEEK
from nott_your_timetable.utils.data import get_data
from nott_your_timetable.utils.parsers import get_program_value, \
    AmbiguousProgramError
from nott_your_timetable.utils.range_handlers import handle_ranges, \
    handle_ranges_days

COURSE = ["-c", "E & EE", "some program"]
EEE = ["-c", "E & EE", "BEng Hons Electl & Electnc Eng/F/02 - H603 "
       "Electrical and Electronic Engineering"]


@pytest.fixture(name="fake_fetch")
def fixture_fake_fetch(monkeypatch, eee_report):
    """Serves the captured report instead of hitting the server."""
    calls = []

    def fake(program_value):
        calls.append(program_value)
        return eee_report

    monkeypatch.setattr(app, "fetch_timetable", fake)
    return calls


def test_main_cli_export(fake_fetch, tmp_path):
    output = tmp_path / "timetable.ics"
    assert app.main_cli(EEE + ["-w", "4", "-d", "1", "-o", str(output)]) == 0

    assert fake_fetch == [get_program_value(*EEE[1:])]
    text = output.read_text(encoding="utf-8")
    assert "DTSTART;TZID=Asia/Kuala_Lumpur:20250922T140000" in text
    assert not (tmp_path / "timetable.ics.ics").exists()


@pytest.mark.usefixtures("fake_fetch")
def test_main_cli_week1_override(tmp_path):
    output = tmp_path / "timetable"
    assert app.main_cli(EEE + ["-w", "4", "-d", "1", "--week1", "2026-09-07",
                               "-o", str(output)]) == 0
    text = (tmp_path / "timetable.ics").read_text(encoding="utf-8")
    assert "DTSTART;TZID=Asia/Kuala_Lumpur:20260928T140000" in text


def test_main_cli_server_rejects(monkeypatch, capsys):
    def reject(program_value):
        raise requests.HTTPError("400 Client Error")

    monkeypatch.setattr(app, "fetch_timetable", reject)
    assert app.main_cli(EEE) == 1
    assert "program list may be outdated" in capsys.readouterr().err


def test_main_cli_invalid_program(fake_fetch):
    assert app.main_cli(COURSE) == 1
    assert not fake_fetch


@pytest.mark.parametrize("output, export_format, expected", [
    (None, "ics", None),
    ("timetable", "ics", "timetable.ics"),
    ("timetable.ics", "ics", "timetable.ics"),
    ("timetable.ICS", "ics", "timetable.ICS"),
    ("timetable.csv", "ics", "timetable.csv.ics"),
    ("my.timetable", "csv", "my.timetable.csv"),
])
def test_output_filename(output, export_format, expected):
    assert output_filename(output, export_format) == expected


def test_week1_argument():
    args = parse_arguments(COURSE + ["--week1", "2026-09-07"])
    assert args.week1 == datetime.date(2026, 9, 7)
    assert parse_arguments(COURSE).week1 is None


def test_week1_argument_invalid():
    with pytest.raises(SystemExit):
        parse_arguments(COURSE + ["--week1", "07/09/2026"])


def test_this_week_is_deferred():
    assert parse_arguments(COURSE + ["-tw"]).weeks == THIS_WEEK


@pytest.mark.parametrize("school, program", [
    ("Central", "anything"),        # School/division without programs
    ("E & EE", "Not a program"),
    ("Not a school", "anything"),
])
def test_get_program_value_invalid(school, program):
    with pytest.raises(ValueError):
        get_program_value(school, program)


FOUNDATION = "Foundation Programme/F/00 - Foundation Foundation Programme"


@pytest.mark.parametrize("program, expected", [
    ("BEng Hons Electl & Electnc Eng/F/02 - H603 Electrical and Electronic "
     "Engineering", "UG/M1024/M6UEEENG/F/02"),
    ("UG/M1024/M6UEEENG/F/02", "UG/M1024/M6UEEENG/F/02"),   # Raw id
])
def test_get_program_value(program, expected):
    assert get_program_value("E & EE", program) == expected


def test_get_program_value_duplicate_names():
    school = next(name for name, value in get_data()[0].items()
                  if value == "MSC-FNDS")
    assert get_program_value(
        school, f"{FOUNDATION} [FND/M1305/M5UFDNSAPR/F/00]"
    ) == "FND/M1305/M5UFDNSAPR/F/00"

    with pytest.raises(AmbiguousProgramError) as err:
        get_program_value(school, FOUNDATION)
    assert sorted(err.value.candidates) == [
        f"{FOUNDATION} [FND/M1305/M5UFDNSAPR/F/00]",
        f"{FOUNDATION} [FND/M1306/M5UFDNSSEP/F/00]",
    ]


def test_main_cli_ambiguous_program(fake_fetch, capsys):
    school = next(name for name, value in get_data()[0].items()
                  if value == "MSC-FNDS")
    assert app.main_cli(["-c", school, FOUNDATION]) == 1
    assert not fake_fetch
    assert "FND/M1306/M5UFDNSSEP/F/00" in capsys.readouterr().err


@pytest.mark.parametrize("value, expected", [
    ("1-3", [1, 2, 3]),
    ("4-15, 22-33", list(range(4, 16)) + list(range(22, 34))),
    ("5,1,3", [1, 3, 5]),
    ("3-1", [1, 2, 3]),
])
def test_handle_ranges(value, expected):
    assert handle_ranges(value) == expected


@pytest.mark.parametrize("value, expected", [
    ("Mon-Fri", [1, 2, 3, 4, 5]),
    ("6-7", [6, 7]),
    ("1, 3", [1, 3]),
])
def test_handle_ranges_days(value, expected):
    assert handle_ranges_days(value) == expected


@pytest.mark.parametrize("value", ["a", "1-b", "1,,2"])
def test_handle_ranges_invalid(value):
    with pytest.raises(ValueError):
        handle_ranges(value)
