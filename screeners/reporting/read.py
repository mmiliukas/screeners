import pandas as pd

from screeners.config import config


def read_tickers():
    names = [f"{x['name']} First Seen" for x in config["screeners"]]
    names.append("Screener First Seen")

    source = config["tickers"]["target"]
    current = pd.read_csv(source, parse_dates=names)

    for name in names:
        current[name] = current[name].dt.date

    source = "https://raw.githubusercontent.com/mmiliukas/screeners/main/" + source
    previous = pd.read_csv(source, parse_dates=names)

    for name in names:
        previous[name] = previous[name].dt.date

    return [current, previous]


def read_ignored_tickers():
    source = config["ignored_tickers"]["target"]
    current = pd.read_csv(source, parse_dates=["Date"])
    current["Date"] = current["Date"].dt.date

    source = "https://raw.githubusercontent.com/mmiliukas/screeners/main/" + source
    previous = pd.read_csv(source, parse_dates=["Date"])
    previous["Date"] = previous["Date"].dt.date

    return [current, previous]
