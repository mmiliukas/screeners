import pandas as pd

import screeners.report as re
from screeners.config import config


def read_tickers() -> pd.DataFrame:
    names = [f"{x['name']} First Seen" for x in config["screeners"]]
    names.append("Screener First Seen")

    source = config["tickers"]["target"]
    current = pd.read_csv(source, parse_dates=names)

    for name in names:
        current[name] = current[name].dt.date

    return current


def read_ignored_tickers() -> pd.DataFrame:
    source = config["ignored_tickers"]["target"]
    current = pd.read_csv(source, parse_dates=["Date"])
    current["Date"] = current["Date"].dt.date

    return current


def build_reports(tickers: pd.DataFrame, ignored_tickers: pd.DataFrame) -> None:
    df = re.calendar()
    df.to_csv("./reports/calendar.csv", float_format="%.0f")

    df = re.first_seen(tickers, ignored_tickers)
    df.to_csv("./reports/first-seen.csv", float_format="%.0f")

    df = re.etfs_close()
    df.to_csv("./reports/etfs-close.csv", float_format="%.2f")

    df = re.tickers_by_sector(tickers)
    df.to_csv("./reports/tickers-sector.csv", float_format="%.2f")

    df = re.tickers_by_price(tickers)
    df.to_csv("./reports/tickers-price.csv", float_format="%.2f")

    df = re.tickers_by_screener(tickers)
    df.to_csv("./reports/tickers-screener.csv", float_format="%.2f")

    df = re.tickers_ignored(ignored_tickers)
    df.to_csv("./reports/tickers-ignored.csv", float_format="%.2f")

    df = re.pnk_by_sector(tickers)
    df.to_csv("./reports/pnk-by-sector.csv", float_format="%.2f")

    df = re.pnk_by_screener(tickers)
    df.to_csv("./reports/pnk-by-screener.csv", float_format="%.2f")

    df = re.exchanges(tickers, ignored_tickers)
    df.to_csv("./reports/exchanges.csv", float_format="%.2f")


def reports() -> None:
    tickers = read_tickers()
    ignored_tickers = read_ignored_tickers()

    build_reports(tickers, ignored_tickers)
