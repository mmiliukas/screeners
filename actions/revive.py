from datetime import date, timedelta
from time import sleep

import pandas as pd
import yfinance as yf
from tqdm import tqdm

from screeners.config import config
from screeners.download import download
from screeners.utils import abs_path


def is_ticker_alive(symbol: str, ticker: yf.Ticker) -> bool:
    # 404
    if not ticker.info:
        return False

    # 404
    if ticker.info.get("symbol") != symbol:
        return False

    # not categorized
    if not ticker.info.get("sector"):
        return False

    # ratio below X
    current_ratio = ticker.info.get("currentRatio", 0)
    if current_ratio < config.scraper.min_current_ratio:
        return False

    # not being traded anymore, no trades in the last X days
    start = date.today() - timedelta(days=config.scraper.min_trading_days)
    history = download(symbol, start=start, interval="1d")

    if len(history) == 0:
        return False

    # not enough data
    first_seen = pd.read_csv(abs_path("first-seen/", symbol + ".csv"))
    if len(first_seen) == 0:
        return False

    return True


def revive() -> None:
    target = config.ignored_tickers.target

    df = pd.read_csv(target, parse_dates=["Date"])
    df["Date"] = df["Date"].dt.date

    ignore_after_date = date.today() - timedelta(days=config.revive.ignore_after_days)
    df = df[df["Date"] > ignore_after_date]

    revived = []

    with tqdm(total=len(df)) as progress:
        for symbol in df["Symbol"].values:

            ticker = yf.Ticker(symbol)

            if is_ticker_alive(symbol, ticker):
                revived.append(symbol)

            progress.set_description(f"{symbol:>10}", refresh=False)
            progress.update(1)

            sleep(config.revive.sleep)

    df = pd.read_csv(target)
    df = df[~df["Symbol"].isin(revived)]
    df.to_csv(target, index=False)
