"""Tests for parsing the timetable report and exporting it."""
# pylint: disable=missing-function-docstring
import csv
import datetime
import io
import pytest
from icalendar import Calendar
from nott_your_timetable.utils import weeks
from nott_your_timetable.utils.parsers import parse_response, TIMEZONE

ALL_DAYS = list(range(1, 8))
ALL_WEEKS = list(range(1, 53))
MODULE = "Electrical Energy Conditioning and Control"


def events_of(data, subject):
    """Returns sorted (date, start, end, location) of a subject."""
    return sorted(
        (data["Start Date"][i], data["Start Time"][i], data["End Time"][i],
         data["Location"][i])
        for i, name in enumerate(data["Subject"]) if name == subject
    )


def test_parse_full_year(eee_report):
    data = parse_response(eee_report, ALL_DAYS.copy(), ALL_WEEKS)

    assert len(data["Subject"]) == 262
    lengths = {len(data[key]) for key in
               ("Subject", "Start Date", "Start Time", "End Time",
                "Location")}
    assert lengths == {262}


def test_dates_use_week1_from_report(eee_report):
    data = parse_response(eee_report, ALL_DAYS.copy(), ALL_WEEKS)

    # Monday lecture in weeks 4-6, 8-9 -> week 4 is 22 Sep 2025
    first = events_of(data, MODULE)[0]
    assert first == (datetime.date(2025, 9, 22), datetime.time(14, 0),
                     datetime.time(16, 0), "BlockF3-F3A04+")


def test_week1_is_recorded(eee_report):
    data = parse_response(eee_report, ALL_DAYS.copy(), ALL_WEEKS)
    assert data.week1 == datetime.date(2025, 9, 1)


def test_current_week(eee_report, monkeypatch):
    class FakeDate(datetime.date):
        """Pins today to Monday of week 4."""
        @classmethod
        def today(cls):
            return cls(2025, 9, 24)

    monkeypatch.setattr(weeks.datetime, "date", FakeDate)
    data = parse_response(eee_report, ALL_DAYS.copy(), None)

    assert data["Subject"]
    assert {d.isocalendar()[1] for d in data["Start Date"]} == \
        {datetime.date(2025, 9, 22).isocalendar()[1]}


def test_week1_override(eee_report):
    data = parse_response(eee_report, ALL_DAYS.copy(), ALL_WEEKS,
                          week1=datetime.date(2026, 9, 7))
    assert events_of(data, MODULE)[0][0] == datetime.date(2026, 9, 28)


def test_filter_days(eee_report):
    data = parse_response(eee_report, [1], ALL_WEEKS)

    assert data["Subject"]
    assert {d.isoweekday() for d in data["Start Date"]} == {1}


def test_filter_weeks(eee_report):
    week1 = datetime.date(2025, 9, 1)
    data = parse_response(eee_report, ALL_DAYS.copy(), [4])

    assert data["Subject"]
    assert all(week1 + datetime.timedelta(weeks=3) <= d
               < week1 + datetime.timedelta(weeks=4)
               for d in data["Start Date"])


def test_no_classes_outside_teaching_weeks(eee_report):
    assert parse_response(eee_report, ALL_DAYS.copy(), [1, 2])["Subject"] \
        == []


def test_export_ical_timezone(eee_report, tmp_path):
    data = parse_response(eee_report, [1], [4])
    output = tmp_path / "out.ics"
    assert data.export("ics", str(output)) == 0

    cal = Calendar.from_ical(output.read_bytes())
    timezones = [tz["TZID"] for tz in cal.walk("VTIMEZONE")]
    assert timezones == ["Asia/Kuala_Lumpur"]

    events = cal.walk("VEVENT")
    assert len(events) == len(data["Subject"])
    event = next(e for e in events if e["SUMMARY"] == MODULE)
    start = event["DTSTART"].dt
    assert start == datetime.datetime(2025, 9, 22, 14, tzinfo=TIMEZONE)
    assert start.utcoffset() == datetime.timedelta(hours=8)
    assert event["DTSTART"].params["TZID"] == "Asia/Kuala_Lumpur"
    assert event["DTSTAMP"].dt.utcoffset() == datetime.timedelta(0)


def test_export_ical_unique_uids(eee_report, tmp_path):
    data = parse_response(eee_report, ALL_DAYS.copy(), ALL_WEEKS)
    output = tmp_path / "out.ics"
    data.export("ics", str(output))

    uids = [e["UID"] for e in
            Calendar.from_ical(output.read_bytes()).walk("VEVENT")]
    assert len(uids) == len(set(uids))


def test_export_csv(eee_report, tmp_path):
    data = parse_response(eee_report, [1], [4])
    output = tmp_path / "out.csv"
    assert data.export("csv", str(output)) == 0

    rows = list(csv.reader(io.StringIO(output.read_text(encoding="utf-8"))))
    assert rows[0][:5] == ["Subject", "Start Date", "Start Time",
                           "End Date", "End Time"]
    assert len(rows) - 1 == len(data["Subject"])
    # Sorted by date then time
    keys = [(row[1], row[2]) for row in rows[1:]]
    assert keys == sorted(keys)
    assert [MODULE, "2025-09-22", "14:00:00"] in [row[:3] for row in rows]


def test_export_invalid_format(eee_report):
    data = parse_response(eee_report, [1], [4])
    assert data.export("vcard", None) == 1


@pytest.mark.parametrize("response", ["", "<html><body></body></html>"])
def test_parse_empty_response(response):
    assert parse_response(response, ALL_DAYS.copy(), ALL_WEEKS)["Subject"] \
        == []
