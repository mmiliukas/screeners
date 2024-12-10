import datetime
import json
import logging
from glob import glob

import pandas as pd
import yfinance as yf
from tqdm import tqdm

from screeners.config import config
from screeners.etfs import get_etfs_and_holdings
from screeners.utils import abs_path

logger = logging.getLogger(__name__)


def refresh() -> None:

    runs = [screener.cache_name for screener in config.screeners]
    csvs = [csv for run in runs for csv in glob(f"{run}/*.csv")]

    dfs = [pd.read_csv(csv) for csv in csvs]
    df = pd.concat([df for df in dfs if not df.empty])

    tickers = list(df["Symbol"].unique())
    all_tickers = tickers + get_etfs_and_holdings()

    with tqdm(total=len(all_tickers)) as progress:
        for ticker in all_tickers:
            progress.update(1)

            path = abs_path(config.tickers.cache_name, ticker + ".json")
            yf_ticker = yf.Ticker(ticker)
            with open(path, "w") as file:
                info = yf_ticker.info
                info["__fetch_time"] = datetime.date.today().isoformat()

                file.write(json.dumps([info]))
