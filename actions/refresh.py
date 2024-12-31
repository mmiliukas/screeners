import datetime
import json
import logging
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
        fetch_time = json.load(file)[0].get("__fetch_time")
    fetch_time = datetime.date.fromisoformat(fetch_time)
    today = datetime.date.today()
    return (today - fetch_time).days


def is_outdated(pah: str) -> bool:
    return last_fetched_in_days(pah) > config.tickers.refresh_in_days


def refresh() -> None:

    runs = [screener.cache_name for screener in config.screeners]
    csvs = [csv for run in runs for csv in glob(f"{run}/*.csv")]

    dfs = [pd.read_csv(csv) for csv in csvs]
    df = pd.concat([df for df in dfs if not df.empty])

    tickers = list(df["Symbol"].unique())
    all_tickers = tickers + get_etfs_and_holdings()

    ignored = pd.read_csv(config.ignored_tickers.target)

    processed = 0

    for ticker in all_tickers:
        if len(ignored[ignored["Symbol"] == ticker]) != 0:
            logger.info(f"{ticker:>20} ignored")
            continue

        path = abs_path(config.tickers.cache_name, ticker + ".json")
        if not is_outdated(path):
            logger.info(f"{ticker:>20} cache hit")
            continue

        processed += 1
        if processed > config.tickers.refresh_limit:
            return

        yf_ticker = yf.Ticker(ticker)
        with open(path, "w") as file:
            info = yf_ticker.info
            info["__fetch_time"] = datetime.date.today().isoformat()

            file.write(json.dumps([info]))
            logger.info(
                f"{ticker:>20} {processed:>4}/{config.tickers.refresh_limit} refreshed"
            )

            sleep(1)
