import datetime
import json
import logging
import os.path
from glob import glob

import pandas as pd
import yfinance as yf
from tqdm import tqdm

from screeners.config import config
from screeners.download import download
from screeners.etfs import get_etfs_and_holdings
from screeners.utils import abs_path

logger = logging.getLogger(__name__)


def read_csv(file: str) -> pd.DataFrame:
    return pd.read_csv(file, parse_dates=["Date"])


def tickers() -> None:

    runs = [screener.cache_name for screener in config.screeners]
    csvs = [csv for run in runs for csv in glob(f"{run}/*.csv")]

    dfs = [read_csv(csv) for csv in csvs]
    df = pd.concat([df for df in dfs if not df.empty])

    tickers = list(df["Symbol"].unique())
    all_tickers = tickers + get_etfs_and_holdings()

    logger.info(f"downloading missing tickers...")

    with tqdm(total=len(all_tickers)) as progress:
        for ticker in all_tickers:
            progress.update(1)

            path = abs_path(config.tickers.cache_name, ticker + ".json")
            if os.path.exists(path):
                continue

            yf_ticker = yf.Ticker(ticker)
            with open(path, "w") as file:
                info = yf_ticker.info
                info["__fetch_time"] = datetime.date.today().isoformat()

                file.write(json.dumps([info]))

    logger.info(f"downloading missing first seen details...")

    with tqdm(total=len(tickers)) as progress:
        for ticker in tickers:
            progress.update(1)

            path = abs_path("first-seen/", ticker + ".csv")
            if os.path.exists(path):
                continue

            end = df[df["Symbol"] == ticker]["Date"].min()
            start = end - pd.Timedelta(days=config.scraper.min_trading_days)

            download(ticker, start, end).to_csv(path)
