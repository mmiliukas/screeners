import pandas as pd

from screeners.config import config


def read_tickers():
    source = config["tickers"]["target"]
    current = pd.read_csv(source, parse_dates=["Screener First Seen"])
    current["Screener First Seen"] = current["Screener First Seen"].dt.date

    source = "https://raw.githubusercontent.com/mmiliukas/screeners/main/" + source
    previous = pd.read_csv(source, parse_dates=["Screener First Seen"])
    previous["Screener First Seen"] = previous["Screener First Seen"].dt.date

    return (current, previous)


def read_ignored_tickers():
    source = config["ignored_tickers"]["target"]
    current = pd.read_csv(source, parse_dates=["Date"])
    current["Date"] = current["Date"].dt.date

    source = "https://raw.githubusercontent.com/mmiliukas/screeners/main/" + source
    previous = pd.read_csv(source, parse_dates=["Date"])
    previous["Date"] = previous["Date"].dt.date

    return (current, previous)
