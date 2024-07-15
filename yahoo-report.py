#!/usr/bin/env python

import logging
import logging.config
import sys
from datetime import date

import yaml

from screeners.report import (
    calendar,
    etfs_close,
    exchanges,
    first_seen,
    pnk_by_screener,
    pnk_by_sector,
    tickers_by_price,
    tickers_by_screener,
    tickers_by_sector,
)
from screeners.reporting.read import read_ignored_tickers, read_tickers
from screeners.telegram import log_to_telegram

with open("config-logging.yml", "r") as config_logging:
    logging.config.dictConfig(yaml.safe_load(config_logging.read()))


faq = "https://github.com/mmiliukas/screeners/blob/main/FAQ.md"
grafana = "https://mmiliukas.grafana.net/d/b0cf7597-cc5c-4368-b682-92d5e2c505b3/scraping-results"


def main(argv) -> None:
    bot_token, channel_id, run_type = argv[1:]

    message = (
        f"<b>{run_type}:</b> "
        f"{date.today().isoformat()} "
        f"<a href='{faq}'>FAQ</a> "
        f"<a href='{grafana}'>Grafana Charts</a>"
    )
    log_to_telegram(message, bot_token, channel_id)

    tickers = read_tickers()[0]
    ignored_tickers = read_ignored_tickers()[0]

    df = calendar()
    df.to_csv("./reports/calendar.csv", float_format="%.0f")

    df = first_seen(tickers, ignored_tickers)
    df.to_csv("./reports/first-seen.csv", float_format="%.0f")

    df = etfs_close()
    df.to_csv("./reports/etfs-close.csv", float_format="%.2f")

    df = tickers_by_sector(tickers)
    df.to_csv("./reports/tickers-sector.csv", float_format="%.2f")

    df = tickers_by_price(tickers)
    df.to_csv("./reports/tickers-price.csv", float_format="%.2f")

    df = tickers_by_screener(tickers)
    df.to_csv("./reports/tickers-screener.csv", float_format="%.2f")

    df = pnk_by_sector(tickers)
    df.to_csv("./reports/pnk-by-sector.csv", float_format="%.2f")

    df = pnk_by_screener(tickers)
    df.to_csv("./reports/pnk-by-screener.csv", float_format="%.2f")

    df = exchanges(tickers, ignored_tickers)
    df.to_csv("./reports/exchanges.csv", float_format="%.2f")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
