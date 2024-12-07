import datetime
import json
import os.path
from time import sleep

import pandas as pd
import yfinance as yf
from tqdm import tqdm

from screeners.config import config
from screeners.etfs import get_etfs_and_holdings
from screeners.tickers import get_tickers
from screeners.utils import abs_path


def tickers() -> None:
    __fetch_time = datetime.date.today().isoformat()

    tickers = get_tickers()
    tickers.extend(get_etfs_and_holdings())

    ignored_tickers = config.ignored_tickers.target
    cache_name = config.tickers.cache_name

    df = pd.read_csv(ignored_tickers, parse_dates=["Date"])

    with tqdm(total=len(tickers)) as progress:
        for symbol in tickers:

            progress.update(1)

            ticker_path = abs_path(cache_name, symbol + ".json")
            if os.path.exists(ticker_path):
                continue

            sleep(0.3)
            result = yf.Ticker(symbol)

            if not result.info or "symbol" not in result.info:
                if symbol not in df["Symbol"].values:
                    now = datetime.datetime.now()
                    df.loc[len(df.index)] = [symbol, now, "Not Found"]
            else:
                with open(ticker_path, "w") as file:
                    info = result.info
                    info["__fetch_time"] = __fetch_time

                    file.write(json.dumps([info]))

    df.to_csv(ignored_tickers, index=False)
