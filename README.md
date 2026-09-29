# Nott Your Timetable
Exports Timetable for University of Nottingham Malaysia Student.

> **Note:** This is a maintained fork of [ecyht2/nott-your-timetable](https://github.com/ecyht2/nott-your-timetable), which is no longer updated. All credit for the original project goes to ecyht2. Changes are licensed under the same [GPL-3.0](LICENSE) license.

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
**Table of Contents**

- [Nott Your Timetable](#nott-your-timetable)
    - [Installation](#installation)
        - [Windows Folder (Recommended)](#windows-folder-recommended)
        - [Windows Single EXE](#windows-single-exe)
        - [MacOS](#macos)
        - [Installing via Pip](#installing-via-pip)
            - [Requirements](#requirements)
            - [Installation](#installation-1)
    - [Usage](#usage)
        - [GUI](#gui)
        - [Importing Timetable](#importing-timetable)
            - [Outlook](#outlook)
            - [Google Calendar](#google-calendar)
        - [CLI](#cli)
    - [Development](#development)
        - [Updating School/Division and Program Data](#updating-schooldivision-and-program-data)
    - [TODO](#todo)

<!-- markdown-toc end -->

## Installation

### Windows Folder (Recommended)

1. Download the latest version of nott-your-timetable.zip [here](https://github.com/wong80/nott-your-timetable/releases/latest "Download Link").
2. Extract the .zip file.
3. Run the .exe file inside the extracted folder.

### Windows Single EXE

**Note:** Both folder and single exe file has the same features. However, the single exe file might take a longer time to start.

1. Download the latest version of nott-your-timetable.exe [here](https://github.com/wong80/nott-your-timetable/releases/latest "Download Link").
2. Run the .exe file.

### MacOS

**Note:** Both versions have the same features, but the first one might take a longer time to start.

1. Download the latest version of nott-your-timetable-macos.zip or nott-your-timetable-macos-folder.zip (recommended) [here](https://github.com/wong80/nott-your-timetable/releases/latest "Download Link").
2. Extract the .zip file.
3. Move the extracted .app file into `Applications` folder (optional).
4. Run the .app file.

### Installing via Pip

#### Requirements

`python>=3.10` Latest version of Python can be downloaded [here](https://www.python.org/downloads/) for more information

#### Installation

This fork isn't published on PyPI (the `nott-your-timetable` package there is the original, unmaintained version). Install it from GitHub instead:

``` sh
pip install "nott-your-timetable @ git+https://github.com/wong80/nott-your-timetable"
```

For GUI support:

**Note:** there might be some error isntalling PyGObject using pip, follow the instruction [here](https://pygobject.readthedocs.io/en/latest/getting_started.html "PyGObject download") to download gtk. When following the instructions replace all refrences to **gtk3** with **gtk4** as nott-your-timetable uses **gtk4** and not **gtk3** e.g. `mingw-w64-x86_64-gtk3` -> `mingw-w64-x86_64-gtk4`.

``` sh
pip install "nott-your-timetable[gui] @ git+https://github.com/wong80/nott-your-timetable"
```

## Usage

### GUI
1. Select School/Division
![School/Division Selection](https://raw.githubusercontent.com/wong80/nott-your-timetable/master/media/school.jpg)
2. Select Program
![Program Selection](https://raw.githubusercontent.com/wong80/nott-your-timetable/master/media/program.jpg)
3. Select week period
![Weeks Selection](https://raw.githubusercontent.com/wong80/nott-your-timetable/master/media/weeks.jpg)
4. Select day period
![Days Selection](https://raw.githubusercontent.com/wong80/nott-your-timetable/master/media/days.jpg)
5. Select export file format and hit continue. If you are confused just choose **ics**.
![Export Format Selection](https://raw.githubusercontent.com/wong80/nott-your-timetable/master/media/format.jpg)
6. Select location to save.
![Save Location Selection](https://raw.githubusercontent.com/wong80/nott-your-timetable/master/media/save.jpg)

### Importing Timetable

#### Outlook

1. Open Outlook and go to the calendar section.
![Outlook Calendar](https://raw.githubusercontent.com/wong80/nott-your-timetable/master/media/outlook.jpg)
2. Click on add calendar.
![Adding Calendar](https://raw.githubusercontent.com/wong80/nott-your-timetable/master/media/add-calendar.jpg)
3. Click on upload from file.
![Upload from file](https://raw.githubusercontent.com/wong80/nott-your-timetable/master/media/upload.jpg)
4. Select file and calendar to import to.
![Uploading Calendar](https://raw.githubusercontent.com/wong80/nott-your-timetable/master/media/select.jpg)
5. Done :)
![Imported Calendar](https://raw.githubusercontent.com/wong80/nott-your-timetable/master/media/done.jpg)

#### Google Calendar

TODO

### CLI
A simple usage to export the entire year to a ics file by default.

**Note:** The quotes are needed if you are putting spaces inbetween

Gets the timetable for Electrical and Electronic Engineering BEng Year 2:

```sh
nott-your-timetable-cli -c "E & EE" "BEng Hons Electl & Electnc Eng/F/02 - H603 Electrical and Electronic Engineering"
```

Only for week 1 to week 10.

```sh
nott-your-timetable-cli -w '1-10' -c "E & EE" "BEng Hons Electl & Electnc Eng/F/02 - H603 Electrical and Electronic Engineering"
```

Only for Monday to Friday.

```sh
nott-your-timetable-cli -c "E & EE" "BEng Hons Electl & Electnc Eng/F/02 - H603 Electrical and Electronic Engineering" -d 1-5
```

Only for week 4 to week 6 Monday to Friday.

```sh
nott-your-timetable-cli -c "E & EE" "BEng Hons Electl & Electnc Eng/F/02 - H603 Electrical and Electronic Engineering" -d '4, 5, 6' -w 1-5
```

If you don't know what school/division and program, the `-i` flag can be used to ender interactive mode.

```sh
nott-your-timetable-cli -i
```

To export the output to csv
```sh
nott-your-timetable-cli -c "E & EE" "BEng Hons Electl & Electnc Eng/F/02 - H603 Electrical and Electronic Engineering" -f csv
```

Dates are calculated from the start of week 1, which is read from the timetable itself. A warning is shown if the timetable is for a different academic year than today's (e.g. the university hasn't published the new one yet). To override the start of week 1, pass the Monday of week 1:

```sh
nott-your-timetable-cli -c "E & EE" "BEng Hons Electl & Electnc Eng/F/02 - H603 Electrical and Electronic Engineering" --week1 2026-09-07
```

There are more options available, to see all the options use the help argument.

```sh
nott-your-timetable-cli -h
```


## Development

Install with the test dependencies and run the tests:

```sh
pip install -e ".[test]"
pytest
```

### Updating School/Division and Program Data

The list of schools/divisions and programs (`src/nott_your_timetable/data/*.json`) is generated from the timetable server's `js/filter.js`. A scheduled GitHub Action refreshes it weekly and opens a pull request when it changes. To refresh it manually:

```sh
python -m nott_your_timetable.utils.update_data --output-dir src/nott_your_timetable/data
```

Programs that share the same name (e.g. different intakes) have their ID appended, e.g. `Foundation Programme/F/00 - ... [FND/M1305/M5UFDNSAPR/F/00]`. In the CLI, a program can also be selected by its ID alone.

## TODO
  * [ ] Support for exporting to other formats
    * [x] CSV
    * [x] iCalander
    * [ ] vCard
  * [x] Support for other course programs
  * [x] Add more convinience option e.g. Schedule for Spring Semester
  * [x] A graphical frontend
  * [ ] Add GUI and TUI for displaying timetable
  * [x] Make use of [Calender Object](https://docs.python.org/3/library/calendar.html)
  * [x] Tests
  * [x] Automatically update School/Division and Program data
  * [ ] Add Export Options
  * [x] Add better help descriptions
  * [ ] Support for mutiple program selection
  * [ ] Add binaries
    * [ ] EXE (Windows)
      * [x] EXE
      * [ ] Installer
    * [ ] Application (MacOS)
      * [x] App Bundle
      * [ ] DMG
    * [ ] Appimage (Linux)
    * [ ] PKGBUILD (AUR/Arch)
    * [ ] DEB (Debian)
    * [ ] RPM (Red Hat)
    * [ ] Flatpak (Linux) (Maybe?)
    * [ ] Snaps (Linux) (Maybe?)
