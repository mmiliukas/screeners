import json
import logging
import os.path
from datetime import date
from glob import glob

import pandas as pd
import yfinance as yf

from screeners.config import config
from screeners.download import download
from screeners.etfs import get_etfs_and_holdings
from screeners.utils import abs_path

logger = logging.getLogger(__name__)


def read_csv(file: str) -> pd.DataFrame:
    return pd.read_csv(file, parse_dates=["Date"], date_format="%Y-%m-%dT%H:%M:%S.%f")


def tickers() -> None:

    runs = [screener.cache_name for screener in config.screeners]
    csvs = [csv for run in runs for csv in glob(f"{run}/*.csv")]

    dfs = [read_csv(csv) for csv in csvs]
    df = pd.concat([df for df in dfs if not df.empty])

    tickers = list(df["Symbol"].unique())
    all_tickers = sorted(set(tickers + get_etfs_and_holdings()))

    logger.info(f"Downloading missing tickers...")

    for ticker in all_tickers:

        path = abs_path(config.tickers.cache_name, ticker + ".json")
        if os.path.exists(path):
            continue

        logger.info(path)

        yf_ticker = yf.Ticker(ticker)
        with open(path, "w") as file:
            info = yf_ticker.info or {}
            info["__fetch_time"] = date.today().isoformat()

            file.write(json.dumps([info]))

    logger.info(f"Downloading missing first seen details...")

    for ticker in tickers:

        path = abs_path("first-seen/", ticker + ".csv")
        if os.path.exists(path):
            continue

        logger.info(path)

        end = df[df["Symbol"] == ticker]["Date"].min()
        start = end - pd.Timedelta(days=config.scraper.min_trading_days)

        download(ticker, start, end).to_csv(path)
