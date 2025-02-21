from datetime import date, timedelta
from time import sleep

import logging
import pandas as pd
import yfinance as yf
from tqdm import tqdm

from screeners.config import config
from screeners.download import download
from screeners.utils import abs_path

logger = logging.getLogger(__name__)


def is_ticker_alive(symbol: str, ticker: yf.Ticker) -> bool:
    # missing close price
    first_seen = pd.read_csv(abs_path("first-seen/", symbol + ".csv"))
    if first_seen.empty:
        return False

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

            try:
                if is_ticker_alive(symbol, ticker):
                    revived.append(symbol)
            except Exception as check_error:
                logger.errinfoor(f"failed to check ticker {ticker}")

            progress.set_description(f"{symbol:>10}", refresh=True)
            progress.update(1)

            sleep(config.revive.sleep)

    df = pd.read_csv(target)
    df = df[~df["Symbol"].isin(revived)]
    df.to_csv(target, index=False)
