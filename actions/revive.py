import logging
from datetime import date, timedelta

import pandas as pd
import yfinance as yf
from tqdm import tqdm

from screeners.config import config


def __is_ticker_alive(symbol: str, ticker: yf.Ticker) -> bool:
    # 404
    if not ticker.info:
        return False

    # 404
    if ticker.info.get("symbol") != symbol:
        return False

    # not categorized
    if not ticker.info.get("sector"):
        return False

    # ratio below 0.5
    current_ratio = ticker.info.get("currentRatio", 0)
    if current_ratio < 0.5:
        return False

    # not being traded anymore, no trades in the last 5 days
    start = date.today() - timedelta(days=5)

    history = yf.download(symbol, period="max", interval="1d", progress=False)
    history = history[history.index > pd.to_datetime(start)]

    if len(history) == 0:
        return False

    return True


def __revive(df: pd.DataFrame) -> list[str]:
    revived_symbols = []

    with tqdm(total=len(df)) as progress:
        for symbol in df["Symbol"].values:
            ticker = yf.Ticker(symbol)

            if __is_ticker_alive(symbol, ticker):
                revived_symbols.append(symbol)

            progress.set_description(f"{symbol:>10}", refresh=False)
            progress.update(1)

    return revived_symbols


def revive() -> None:
    # ignored tickers generate too much noice, filtering them out
    logging.getLogger("yfinance").setLevel(logging.CRITICAL)

    file_name = config["ignored_tickers"]["target"]
    df = pd.read_csv(file_name)

    revived_symbols = __revive(df)

    df = df[~df["Symbol"].isin(revived_symbols)]
    df.to_csv(file_name, index=False)
