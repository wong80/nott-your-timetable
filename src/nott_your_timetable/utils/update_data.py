#!/usr/bin/env python3
"""Regenerates the School/Division and Program data from the timetable server.

The timetabling system publishes every selectable school and program as
JavaScript arrays in ``js/filter.js``. This module parses those arrays and
writes them in the format used by ``nott_your_timetable/data``.

Usage::

    python -m nott_your_timetable.utils.update_data [--output-dir DIR]
"""
import argparse
import json
import re
import sys
import urllib.request
from importlib.resources import files
from pathlib import Path

FILTER_URL = "http://timetablingunmc.nottingham.ac.uk:8006/js/filter.js"

# Matches lines such as: programmearray[0] [2] = "UG/M1024/M6UEEENG/F/02";
_ASSIGNMENT = re.compile(
    r'\b(?P<array>deptarray|programmearray)\[(?P<row>\d+)\]\s*'
    r'\[(?P<col>\d+)\]\s*=\s*"(?P<value>(?:[^"\\]|\\.)*)"\s*;'
)
_ESCAPE = re.compile(r"\\(.)")


def fetch_filter_js(url: str = FILTER_URL, timeout: float = 30) -> str:
    """Downloads the filter.js file from the timetable server.

    Parameters
    ----------
    url: str
        The url of filter.js
    timeout: float
        Request timeout in seconds

    Returns
    -------
    str
        The contents of filter.js
    """
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return response.read().decode("latin-1")


def _parse_arrays(source: str) -> dict[str, dict[int, dict[int, str]]]:
    """Collects every ``array[row] [col] = "value";`` assignment."""
    arrays: dict[str, dict[int, dict[int, str]]] = {
        "deptarray": {}, "programmearray": {}
    }
    for match in _ASSIGNMENT.finditer(source):
        value = _ESCAPE.sub(r"\1", match["value"])
        arrays[match["array"]].setdefault(int(match["row"]), {})[
            int(match["col"])
        ] = value
    return arrays


def parse_filter_js(source: str) -> tuple[dict[str, str],
                                          dict[str, dict[str, str]]]:
    """Parses filter.js into department and program data.

    Parameters
    ----------
    source: str
        The contents of filter.js

    Returns
    -------
    tuple[dict[str, str], dict[str, dict[str, str]]]
        The department data (name -> id) and program data
        (department id -> program name -> program id), both sorted by key.

    Raises
    ------
    ValueError
        If no departments or programs are found
    """
    arrays = _parse_arrays(source)

    depts = {
        row[0]: row[1] for row in arrays["deptarray"].values()
        if 0 in row and 1 in row
    }

    # Group program ids by department and display name. The same name can
    # map to several ids (e.g. April and September intakes).
    grouped: dict[str, dict[str, set[str]]] = {}
    for row in arrays["programmearray"].values():
        # Skip incomplete rows and placeholders e.g. "Unknown" -> "NULL"
        if not {0, 1, 2} <= row.keys() or row[2] in ("", "NULL") \
                or row[1] not in depts.values():
            continue
        grouped.setdefault(row[1], {}).setdefault(row[0], set()).add(row[2])

    programs: dict[str, dict[str, str]] = {}
    for dept, names in grouped.items():
        for name, ids in names.items():
            if len(ids) == 1:
                programs.setdefault(dept, {})[name] = ids.pop()
            else:
                # Disambiguate duplicate names with their id
                for program_id in ids:
                    programs.setdefault(dept, {})[
                        f"{name} [{program_id}]"
                    ] = program_id

    if not depts or not programs:
        raise ValueError("No department or program data found in filter.js")

    depts = dict(sorted(depts.items()))
    programs = {
        dept: dict(sorted(progs.items()))
        for dept, progs in sorted(programs.items())
    }
    return depts, programs


def write_data(depts: dict, programs: dict, output_dir: Path) -> None:
    """Writes the data to dept.json and program.json.

    Parameters
    ----------
    depts: dict
        The department data
    programs: dict
        The program data
    output_dir: Path
        The directory to write to
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, data in (("dept.json", depts), ("program.json", programs)):
        with open(output_dir / name, "w", encoding="utf-8",
                  newline="\n") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
            file.write("\n")


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--url", default=FILTER_URL,
                        help="URL of filter.js (default: %(default)s)")
    parser.add_argument("--input", type=Path, default=None,
                        help="Parse a local copy of filter.js instead")
    parser.add_argument("--output-dir", type=Path,
                        default=Path(str(files("nott_your_timetable.data"))),
                        help="Directory to write the json files to "
                        "(default: the installed package data)")
    args = parser.parse_args(argv)

    try:
        if args.input is not None:
            source = args.input.read_text(encoding="latin-1")
        else:
            source = fetch_filter_js(args.url)
        depts, programs = parse_filter_js(source)
    except (OSError, ValueError) as err:
        print(f"Failed to update data: {err}", file=sys.stderr)
        return 1

    write_data(depts, programs, args.output_dir)
    print(f"Wrote {len(depts)} schools/divisions and "
          f"{sum(len(p) for p in programs.values())} programs to "
          f"{args.output_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
