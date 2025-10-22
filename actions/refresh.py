import json
import logging
from datetime import date
from glob import glob
from time import sleep

import pandas as pd
import yfinance as yf

from screeners.config import config
from screeners.etfs import get_etfs_and_holdings
from screeners.utils import abs_path

logger = logging.getLogger(__name__)


def last_fetched_in_days(path: str) -> int:
    with open(path, "r") as file:
        fetch_time = json.load(file)[0].get("__fetch_time") or "2024-01-01"
    return (date.today() - date.fromisoformat(fetch_time)).days


def is_outdated(path: str) -> bool:
    return last_fetched_in_days(path) > config.tickers.refresh_in_days


def refresh() -> None:

    logger.info("Loading tickers...")

    runs = [screener.cache_name for screener in config.screeners]
    csvs = [csv for run in runs for csv in glob(f"{run}/*.csv")]

    dfs = [pd.read_csv(csv) for csv in csvs]
    df = pd.concat([df for df in dfs if not df.empty])

    tickers = list(df["Symbol"].unique())
    all_tickers = sorted(set(tickers + get_etfs_and_holdings()))

    logger.info(f"Total unique tickers found '{len(all_tickers)}'...")

    processed = 0

    for index, ticker in enumerate(all_tickers):
        if processed > config.tickers.refresh_limit:
            logging.info("Limit reached, stopping...")
            return

        path = abs_path(config.tickers.cache_name, ticker + ".json")
        if not is_outdated(path):
            logger.info(f"{ticker:>20} {index:>4}/{len(all_tickers)} cache hit")
            continue

        with open(path, "w") as file:
            yf_ticker = yf.Ticker(ticker)

            info = yf_ticker.info or {}
            info["__fetch_time"] = date.today().isoformat()

            file.write(json.dumps([info]))
            logger.info(
                f"{ticker:>20} {processed:>4}/{config.tickers.refresh_limit} refreshed {index}/{len(all_tickers)}"
            )

            processed += 1
            sleep(1)
