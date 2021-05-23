"""test_nmfishingreport.py

Tests for `nmfishingreport` module.
"""

from nmfishingreport import nmfishingreport
import pytest
import os.path
from configparser import ConfigParser
from bs4 import BeautifulSoup


@pytest.fixture(scope="session")
def config():
    test_config = ConfigParser()
    curdir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(curdir, 'test_config.ini')
    test_config.read(config_file)
    return test_config


def test_read_config(config):
    outfile = config["FISHING_REPORT"].get('outfile')
    assert outfile == "fishing_reports_test.txt"


def test_split_conf_str():
    test_str = "   multiline\ntest string """
    test_list = ["multiline", "test string"]
    assert nmfishingreport.split_conf_str(test_str) == test_list


def test_get_current_date():
    soup = BeautifulSoup("""<span class="updated" style="display:none;">
                            2016-05-27T13:50:37+00:00               </span>""",
                        "html.parser")
    cur_date = nmfishingreport.get_current_date(soup)
    assert str(cur_date) == '2016-05-27'


def test_get_current_report():
    url = "http://www.wildlife.state.nm.us/fishing/weekly-report"
    report = nmfishingreport.get_current_report(url)
    title = ("Weekly Fishing & Stocking Report - New Mexico Department of "
             "Game & Fish")
    assert report.title.text == title
