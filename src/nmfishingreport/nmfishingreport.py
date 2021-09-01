"""fishing_report.py :: Scrape NM fishing report into local database.

Pulls fishing reports from NM Dept of Game and Fish, imports into local db.
Puts most recent report from my favorite spots into text file, optionally runs
the `notify` function in `notify_script` if it has the any of the
`notify_words` in the report.
"""

import datetime
import logging
import sqlite3
import urllib.request
from configparser import ConfigParser
from pathlib import Path

import bs4


def split_conf_str(conf_str):
    """Split multiline strings into a list or return an empty list"""
    if conf_str is None:
        return []
    else:
        return conf_str.strip().splitlines()


def get_current_report(url):
    with urllib.request.urlopen(url) as req:
        html = req.read()
    soup = bs4.BeautifulSoup(html, "html.parser")
    return soup


def get_current_date(soup):
    # ":" Gets in the way of strptime parzing the %z
    date_str = soup.find("span", class_="updated").text
    date_str_clean = date_str.replace(":", "").strip()
    cur_dt = datetime.datetime.strptime(date_str_clean, "%Y-%m-%dT%H%M%S%z")
    cur_date = cur_dt.date()
    return cur_date


def main(config_file="config.ini"):
    url = "http://www.wildlife.state.nm.us/fishing/weekly-report"
    config = ConfigParser()
    config.read(config_file)
    fishing_config = config["FISHING_REPORT"]

    logfile = fishing_config.get("logfile", "fishing_report.log")
    logfile = Path(logfile).expanduser()

    logging.basicConfig(
        level=logging.WARNING,
        format=(
            "%(asctime)s %(name)-12s %(lineno)d %(levelname)-8s " "%(message)s"
        ),
        datefmt="%%Y-%%m-%%d %%H:%%M:%%S",
        filename=str(logfile),
        filemode="a",
    )

    logger_name = f'{globals().get("__file__", "")} :: {__name__}'
    logger = logging.getLogger(logger_name)

    # File where results for fav_fishing_spots written as text
    outfile = Path(fishing_config.get("outfile")).expanduser()

    db = Path(fishing_config.get("db", "fishing_reports.db")).expanduser()

    fav_fishing_spots = split_conf_str(fishing_config.get("fav_spots"))

    if config.has_section("NOTIFY"):
        notify_config = config["NOTIFY"]
        notify_words = split_conf_str(notify_config.get("notify_words"))
        notify_script = Path(notify_config.get("notify_script")).expanduser()
    else:
        notify_words = []

    soup = get_current_report(url)
    cur_date = get_current_date(soup)

    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    with conn:
        cmd = """CREATE TABLE IF NOT EXISTS nm_fishing_reports(
                     id INTEGER PRIMARY KEY,
                     date DATE,
                     spot TEXT,
                     report TEXT,
                     UNIQUE (date, spot))"""
        conn.execute(cmd)

        # Get newest date
        cmd = "SELECT date FROM nm_fishing_reports ORDER BY date DESC LIMIT 1"
        old_date = conn.execute(cmd).fetchone()

        # If old date is unset or newer data available
        if old_date is None or cur_date > old_date[0]:
            reports_start = soup.find("h3", text="Message from the Department")
            all_spots = reports_start.find_all_next(
                lambda x: x.name == "p" and x.next.name == "strong"
            )

            spots_dict = {}
            for each_spot in all_spots:
                if ":" in each_spot.text:
                    spot, report = (
                        s.strip() for s in each_spot.text.split(":", 1)
                    )
                else:
                    spot_tag = each_spot.find("strong")
                    spot = spot_tag.text.strip()
                    if sib := spot_tag.next_sibling:
                        report = sib.strip()
                    else:
                        continue

                spots_dict.update({spot: report})

            for spot, report in spots_dict.items():
                infos = (cur_date, spot, report)
                cmd = """INSERT INTO nm_fishing_reports(date, spot, report)
                         VALUES (?,?,?)"""
                logger.debug("Inserting into db: {}, {}, {}".format(*infos))
                conn.execute(cmd, infos)

            # Special stuff for favorite spots
            txt_out = (
                "## NM fishing report for " "{:%a, %b %d, %Y}:\n\n"
            ).format(cur_date)
            for fav_spot in fav_fishing_spots:
                notfound = "Report for {} not found".format(fav_spot)
                fav_report = spots_dict.get(fav_spot, notfound)
                txt_out += "- **{}**: {}\n".format(fav_spot, fav_report)

                if any(
                    word.lower() in fav_report.lower() for word in notify_words
                ):
                    notify_func = notify_script.read_text()
                    exec(notify_func, globals())
                    notify_dict = {
                        "url": url,
                        "spot": fav_spot,
                        "report": fav_report,
                    }
                    notify(notify_dict, config_file=config_file)  # noqa

            if outfile is not None:
                with outfile.open("w") as f:
                    f.write(txt_out)
