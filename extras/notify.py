"""notify.py

Example notification script for fishing_report.py
"""

from configparser import ConfigParser
import urllib.request
import urllib.parse


def notify(notify_dict, config_file="config.ini"):
    config = ConfigParser()
    config.read(config_file)
    notify_config = config["NOTIFY"]
    user = notify_config.get("user")
    api_token = notify_config.get("api_token")

    api_url = "https://api.pushover.net/1/messages.json"

    payload = urllib.parse.urlencode(
        {
            "token": api_token,
            "user": user,
            "message": notify_dict.get("report"),
            "title": notify_dict.get("spot"),
            "url": notify_dict.get("url"),
        }
    )

    with urllib.request.urlopen(api_url, data=payload.encode()) as resp:
        return resp.status == 200
