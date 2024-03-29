# NM Fishing Report

master: [![master branch build
status](https://github.com/n8henrie/nmfishingreport/actions/workflows/python-package.yml/badge.svg?branch=master)](https://github.com/n8henrie/nmfishingreport/actions/workflows/python-package.yml)

Scrapes the NM Dept of Game and Fish fishing report

- Free software: MIT
- Documentation: https://nmfishingreport.readthedocs.org

## Features

- Scrapes fishing report into sqlite database
- Writes to a text file the reports for a specified list of spots
    - Basic Markdown format
    - I use this to output to a Dropbox folder for easy access on mobile
- Monitors for keywords and can optionally use a custom notification script
  when those keywords appear in a report

## Introduction

The NM Dept of Game and Fish publishes [a biweekly fishing
report](http://www.wildlife.state.nm.us/fishing/weekly-report/). This script
scrapes the report into a database so I can see how various spots fare
throughout the year. It send me a [Pushover](https://pushover.net/)
notification whenever the report for one of my favorite spots has any of the
buzzwords I've selected.

## Dependencies

- Python3
- OS X or Linux
- See `requirements.txt`

## Quickstart

1. Copy `config-sample.ini` (recommended: rename to `config.ini`, which is
   `.gitignore`d)
1. Modify config (see section below)
1. `pip3 install nmfishingreport`
1. `python3 -m nmfishingreport -c /path/to/your-config.ini`

### Development Setup

1. Clone the repo: `git clone https://github.com/n8henrie/nmfishingreport && cd
   nmfishingreport`
1. Make a virtualenv: `python3 -m venv .venv`
1. Install dev setup: `./.venv/bin/pip install .[dev]`

## Configuration

I recommend you start with `config-sample.ini`. I've tried to add comments to
make it somewhat self-explanatory. A few notes:

- You'll need to make sure your spelling matches NMDGF for `fav_spots`.
- I've included my database file with some reports going back to 2015
    - There are likely several holes from times when the NMDGF updated their
      website and broke the script or times that my computer wasn't running
    - If you want to want to continue with my existing database, copy it to a
      more reasonable filename (recommended: `fishing_reports.db`), and use it
      as `db` in your config
    - The filename `fishing_reports.db` is `.gitignore`-d
    - I'll try to update the provided file from time to time

### Notification config

If you know a bit of Python, you can optionally provide a notification script
if you want to get a push notification (or email or what have you) when certain
keywords show up in the report for one of your `fav_spots`. The file should
expose a bare function `notify` that accepts two arguemnts:

1. A dictionary containing the following keys:
    - `spot`: the fishing spot triggering the notification
    - `report`: the text of that spot's fishing report
    - `url`: the URL for the fishing report
1. The path to your config file

Because it accepts a path to your config file, you can add a section to your
config file to include usernames and passwords for the notification script if
needed. For example, in the `extras/` directory I've included my (working)
`notify.py` for Pushover -- it pulls my Pushover credentials from my config
file, which is kept out of version control.

Be forewarned that `nmfishingreport` loads the notification script to `exec`ing
its contents, which I'm sure could have security ramifications or lead to data
loss if you aren't careful. Leave the `NOTIFY` section out of your config to
avoid this entirely.

## Acknowledgements

- NM Dept of Game and Fish!

## Troubleshooting / FAQ / Examples

- How can I get info out of an sqlite database?
    - I'm not terribly good at sqlite either, so here's how to convert it to a
      csv file that you can open in your spreadsheet app of choice:
      - `sqlite3 -header -csv fishing_reports.db "SELECT * FROM nm_fishing_reports;" > fishingreport.csv`
- Some other ideas on looking at the contents:
    - Dump all reports to your screen:
        - `sqlite3 fishing_reports.db 'SELECT * FROM nm_fishing_reports;'`
    - Show the 10 most recent reports:
        - `sqlite3 fishing_reports.db 'SELECT * FROM nm_fishing_reports ORDER BY date DESC LIMIT 10;'`
    - Show the 5 most recent reports for the Jemez waters:
        - `sqlite3 fishing_reports.db 'SELECT date, report FROM nm_fishing_reports WHERE spot LIKE "%Jemez%" ORDER BY date DESC LIMIT 5;'`
    - Show the most recent spot to have had the word "excellent" in the report:
        - `sqlite3 fishing_reports.db 'SELECT date, spot FROM nm_fishing_reports WHERE report LIKE "% excellent %" ORDER BY date DESC LIMIT 1;'`
    - Show what times of year the Jemez fishing has been "very good" or
      "excellent":
        - `sqlite3 fishing_reports.db 'SELECT date FROM nm_fishing_reports WHERE (report LIKE "% very good %" OR report LIKE "% excellent %") AND spot LIKE "%Jemez%";'`
- How can I run `nmfishingreport` automatically?
    - If you're on OS X, I've included an example launchd plist in `extras/`
