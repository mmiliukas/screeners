import datetime
import json
import os.path

import pandas as pd
import yfinance as yf
from tqdm import tqdm

from screeners.config import config
from screeners.etfs import get_etfs_and_holdings
from screeners.tickers import get_tickers
from screeners.utils import abs_path


def __should_update(df: pd.DataFrame, symbol: str, ticker_file: str, days: int) -> bool:
    if len(df[df["Symbol"] == symbol]) > 0:
        return False

    if os.path.exists(ticker_file):
        with open(ticker_file, "r") as file:
            ticker = json.load(file)
            if "__fetch_time" in ticker[0]:
                today = datetime.date.today()
                __fetch_time = datetime.date.fromisoformat(ticker[0]["__fetch_time"])

                diff = today - __fetch_time
                if abs(diff.days) < days:
                    return False

    return True


def tickers(days: int) -> None:
    __fetch_time = datetime.date.today().isoformat()

    tickers = get_tickers()
    tickers.extend(get_etfs_and_holdings())

    ignored_tickers = abs_path(config["ignored_tickers"]["target"])
    cache_name = abs_path(config["tickers"]["cache_name"])

    df = pd.read_csv(ignored_tickers, parse_dates=["Date"])

    with tqdm(total=len(tickers)) as progress:
        for symbol in tickers:
            ticker_path = abs_path(cache_name, symbol + ".json")

            if __should_update(df, symbol, ticker_path, days=days):
                result = yf.Ticker(symbol)

                if not result.info or "symbol" not in result.info:
                    now = datetime.datetime.now()
                    df.loc[len(df.index)] = [symbol, now, "Not Found"]
                else:
                    with open(ticker_path, "w") as file:
                        info = result.info
                        info["__fetch_time"] = __fetch_time

                        file.write(json.dumps([info]))

            progress.update(1)

    df.to_csv(ignored_tickers, index=False)
