#!/usr/bin/env python

import logging
import logging.config
import sys
from datetime import date, timedelta

import pandas as pd
import yaml

import screeners.report as re
from screeners.config import config
from screeners.telegram import log_to_telegram

with open("config-logging.yml", "r") as config_logging:
    logging.config.dictConfig(yaml.safe_load(config_logging.read()))


grafana = "https://mmiliukas.grafana.net/d/b0cf7597-cc5c-4368-b682-92d5e2c505b3/scraping-results"
calendar = "https://mmiliukas.grafana.net/d/bdrydrdj6pz40d/trading-calendar"


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


def notify_using_telegram(
    run_type: str,
    bot_token: str,
    channel_id: str,
    tickers: pd.DataFrame,
    ignored_tickers: pd.DataFrame,
) -> None:
    today = date.today()
    yesterday = today - timedelta(days=1)

    today_filtered = tickers[tickers["Screener First Seen"] >= yesterday]
    today_ignored = ignored_tickers[ignored_tickers["Date"] >= yesterday]

    added = ", ".join(today_filtered["Symbol"].values)
    removed = ", ".join(today_ignored["Symbol"].values)

    message = "\n".join(
        [
            f"🟢 <b>{run_type}:</b> {today.isoformat()}",
            f"",
            f"🔗 <a href='{grafana}'>Scraping Results</a>",
            f"🔗 <a href='{calendar}'>Trading Calendar</a>",
            f"",
            f"Tickers for the last 2 days (today + yesterday).",
            f"",
            f"➕ {added if added else 'None'}",
            f"➖ {removed if removed else 'None'}",
        ]
    )
    log_to_telegram(message, bot_token, channel_id)


def main(argv) -> None:
    bot_token, channel_id, run_type = argv[1:]

    tickers = read_tickers()
    ignored_tickers = read_ignored_tickers()

    build_reports(tickers, ignored_tickers)
    notify_using_telegram(run_type, bot_token, channel_id, tickers, ignored_tickers)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
