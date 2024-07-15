#!/usr/bin/env python

import logging
import logging.config
import sys
from datetime import date

import yaml

import screeners.report as re
from screeners.reporting.read import read_ignored_tickers, read_tickers
from screeners.telegram import log_to_telegram

with open("config-logging.yml", "r") as config_logging:
    logging.config.dictConfig(yaml.safe_load(config_logging.read()))


grafana = "https://mmiliukas.grafana.net/d/b0cf7597-cc5c-4368-b682-92d5e2c505b3/scraping-results"


def main(argv) -> None:
    bot_token, channel_id, run_type = argv[1:]

    tickers = read_tickers()[0]
    ignored_tickers = read_ignored_tickers()[0]

    today = date.today()
    today_filtered = tickers[tickers["Screener First Seen"] == date.today()]
    today_ignored = ignored_tickers[ignored_tickers["Date"] == date.today()]

    message = (
        f"<b>{run_type}:</b> {today.isoformat()}<br/>"
        f"<a href='{grafana}' target='_blank'>Grafana Charts</a><br/> "
        f"<code>"
        f"Filtered: {','.join(today_filtered['Symbol'].values)}"
        f" Ignored: {','.join(today_ignored['Symbol'].values)}"
        f"</code>"
    )
    log_to_telegram(message, bot_token, channel_id)

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

    df = re.pnk_by_sector(tickers)
    df.to_csv("./reports/pnk-by-sector.csv", float_format="%.2f")

    df = re.pnk_by_screener(tickers)
    df.to_csv("./reports/pnk-by-screener.csv", float_format="%.2f")

    df = re.exchanges(tickers, ignored_tickers)
    df.to_csv("./reports/exchanges.csv", float_format="%.2f")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
