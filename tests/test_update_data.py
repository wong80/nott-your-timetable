"""Tests for regenerating the School/Division and Program data."""
# pylint: disable=missing-function-docstring
import json
import pytest
from nott_your_timetable.utils.data import get_data
from nott_your_timetable.utils.update_data import parse_filter_js, \
    write_data, main

FILTER_JS = r'''
// Generated Automatically on 7 Oct 2025 10:22:18
var programmearray = new Array(4);
function PopulateFilter(strZoneOrDept, cbxFilter) {
    var deptarray = new Array(3);
    deptarray[0] [0] = "E & EE";
    deptarray[0] [1] = "MSC-EEE";
    deptarray[1] [0] = "Central";
    deptarray[1] [1] = "%23SPLUS2";
    deptarray[2] [0] = "Foundation";
    deptarray[2] [1] = "MSC-FNDS";
    var progfilterarray = new Array(1);
    progfilterarray[0] [0] = "Ignored/F/01";
    progfilterarray[0] [1] = "Ignored/F/01";
}
    programmearray[0] [0] = "BEng Hons Electl & Electnc Eng/F/02 - H603 EEE";
    programmearray[0] [1] = "MSC-EEE";
    programmearray[0] [2] = "UG/M1024/M6UEEENG/F/02";
    programmearray[1] [0] = "Foundation/F/00 - Foundation";
    programmearray[1] [1] = "MSC-FNDS";
    programmearray[1] [2] = "FND/SEP/F/00";
    programmearray[2] [0] = "Foundation/F/00 - Foundation";
    programmearray[2] [1] = "MSC-FNDS";
    programmearray[2] [2] = "FND/APR/F/00";
    programmearray[3] [0] = "Quoted \"Name\"";
    programmearray[3] [1] = "MSC-EEE";
    programmearray[3] [2] = "Q/1";
    programmearray[4] [0] = "#SPLUS019416 - ";
    programmearray[4] [1] = "Unknown";
    programmearray[4] [2] = "NULL";
    programmearray[5] [0] = "Orphan/F/01";
    programmearray[5] [1] = "MSC-NOTADEPT";
    programmearray[5] [2] = "O/1";
'''


def test_parse_filter_js():
    depts, programs = parse_filter_js(FILTER_JS)

    assert depts == {"Central": "%23SPLUS2", "E & EE": "MSC-EEE",
                     "Foundation": "MSC-FNDS"}
    # Placeholder and orphaned programs are dropped
    assert set(programs) == {"MSC-EEE", "MSC-FNDS"}
    assert list(depts) == sorted(depts)
    assert programs["MSC-EEE"] == {
        "BEng Hons Electl & Electnc Eng/F/02 - H603 EEE":
            "UG/M1024/M6UEEENG/F/02",
        'Quoted "Name"': "Q/1",
    }


def test_duplicate_names_are_disambiguated():
    _, programs = parse_filter_js(FILTER_JS)

    assert programs["MSC-FNDS"] == {
        "Foundation/F/00 - Foundation [FND/APR/F/00]": "FND/APR/F/00",
        "Foundation/F/00 - Foundation [FND/SEP/F/00]": "FND/SEP/F/00",
    }


def test_parse_filter_js_empty():
    with pytest.raises(ValueError):
        parse_filter_js("var nothing = 1;")


def test_main_writes_json(tmp_path):
    source = tmp_path / "filter.js"
    source.write_text(FILTER_JS, encoding="latin-1")

    assert main(["--input", str(source), "--output-dir",
                 str(tmp_path / "out")]) == 0
    depts = json.loads((tmp_path / "out" / "dept.json").read_text("utf-8"))
    programs = json.loads(
        (tmp_path / "out" / "program.json").read_text("utf-8")
    )
    assert depts["E & EE"] == "MSC-EEE"
    assert len(programs["MSC-FNDS"]) == 2


def test_main_bad_input(tmp_path):
    assert main(["--input", str(tmp_path / "missing.js"),
                 "--output-dir", str(tmp_path)]) == 1


def test_write_data_is_stable(tmp_path):
    depts, programs = parse_filter_js(FILTER_JS)
    write_data(depts, programs, tmp_path)
    first = (tmp_path / "program.json").read_bytes()
    write_data(depts, programs, tmp_path)
    assert (tmp_path / "program.json").read_bytes() == first
    assert first.endswith(b"}\n") and b"\r\n" not in first


def test_bundled_data_is_consistent():
    depts, programs = get_data()

    assert depts and programs
    # Every program belongs to a known school/division
    assert set(programs) <= set(depts.values())
    # Program ids are unique
    ids = [pid for progs in programs.values() for pid in progs.values()]
    assert len(ids) == len(set(ids))
