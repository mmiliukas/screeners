import datetime
import json
import logging
from glob import glob

import pandas as pd
from tqdm import tqdm

from screeners.config import config
from screeners.utils import abs_path

logger = logging.getLogger(__name__)


def ignore_ticker(ticker: str, reason: str) -> None:
    now = datetime.datetime.now().isoformat()

    ignored_target = config.ignored_tickers.target
    ignored = pd.read_csv(ignored_target)

    if len(ignored[ignored["Symbol"] == ticker]) == 0:
        ignored.loc[len(ignored.index)] = [ticker, now, reason]
        ignored.to_csv(ignored_target, index=False)


def read_ticker(ticker: str) -> dict:
    path = abs_path(config.tickers.cache_name, ticker + ".json")
    with open(path, "r") as file:
        return json.load(file)[0]


def read_first_seen(ticker: str) -> pd.DataFrame:
    path = abs_path("first-seen/", ticker + ".csv")
    return pd.read_csv(path)


def ignore() -> None:

    runs = [screener.cache_name for screener in config.screeners]
    csvs = [csv for run in runs for csv in glob(f"{run}/*.csv")]

    dfs = [pd.read_csv(csv) for csv in csvs]
    df = pd.concat([df for df in dfs if not df.empty])

    tickers = list(df["Symbol"].unique())

    with tqdm(total=len(tickers)) as progress:
        for ticker in tickers:
            progress.update(1)

            result = read_ticker(ticker)
            if result.get("symbol") != ticker:
                ignore_ticker(ticker, "Not Found")
                continue

            if not result.get("sector"):
                ignore_ticker(ticker, "Not Categorized")
                continue

            if result.get("currentRatio", 0) < config.scraper.min_current_ratio:
                ignore_ticker(ticker, "Current Ratio Below 0.5")
                continue

            result = read_first_seen(ticker)
            if len(result) == 0:
                ignore_ticker(ticker, "Missing Close Price")
                continue
