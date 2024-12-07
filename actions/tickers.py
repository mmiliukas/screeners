import datetime
import json
import logging
import os.path
from time import sleep

import pandas as pd
import yfinance as yf
from tqdm import tqdm

from screeners.config import config
from screeners.etfs import get_etfs_and_holdings
from screeners.tickers import get_tickers
from screeners.utils import abs_path

logger = logging.getLogger(__name__)


def tickers() -> None:
    __fetch_time = datetime.date.today().isoformat()

    tickers = get_tickers()
    tickers.extend(get_etfs_and_holdings())

    ignored_tickers = config.ignored_tickers.target
    cache_name = config.tickers.cache_name

    df = pd.read_csv(ignored_tickers, parse_dates=["Date"])

    for symbol in tickers:

        ticker_path = abs_path(cache_name, symbol + ".json")
        if os.path.exists(ticker_path):
            logger.info(f"skipping {symbol} as it already exists")
            continue

        sleep(0.3)
        result = yf.Ticker(symbol)

        if not result.info or "symbol" not in result.info:
            logger.info(f"{symbol} not found")
            if symbol not in df["Symbol"].values:
                logger.info(f"ignoring {symbol}")
                now = datetime.datetime.now()
                df.loc[len(df.index)] = [symbol, now, "Not Found"]
        else:
            logger.info(f"downloading ticker {symbol}")
            with open(ticker_path, "w") as file:
                info = result.info
                info["__fetch_time"] = __fetch_time

                file.write(json.dumps([info]))

    df.to_csv(ignored_tickers, index=False)
