import pandas as pd
from datetime import datetime, timedelta

from screeners.config import config


def previous_source(source: str) -> str:
    with open(".last_report_commit", "r") as file:
        last_commit = (file.readline() or "main").strip()
    base_url = "https://raw.githubusercontent.com/mmiliukas/screeners"
    return f"{base_url}/{last_commit}/{source}".strip()


def read_tickers():
    names = [f"{x['name']} First Seen" for x in config["screeners"]]
    names.append("Screener First Seen")

    source = config["tickers"]["target"]
    current = pd.read_csv(source, parse_dates=names)

    for name in names:
        current[name] = current[name].dt.date

    source = previous_source(source)
    previous = pd.read_csv(source, parse_dates=names)

    for name in names:
        previous[name] = previous[name].dt.date

    return [current, previous]


def read_ignored_tickers():
    source = config["ignored_tickers"]["target"]
    current = pd.read_csv(source, parse_dates=["Date"])
    current["Date"] = current["Date"].dt.date

    source = previous_source(source)
    previous = pd.read_csv(source, parse_dates=["Date"])
    previous["Date"] = previous["Date"].dt.date

    return [current, previous]
