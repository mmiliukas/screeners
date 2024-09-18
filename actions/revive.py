from datetime import date, timedelta

import pandas as pd
import yfinance as yf
from tqdm import tqdm

from screeners.config import config
from screeners.utils import abs_path


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

    # ratio below X
    current_ratio = ticker.info.get("currentRatio", 0)
    if current_ratio < config["scraper"]["min_current_ratio"]:
        return False

    # not being traded anymore, no trades in the last X days
    start = date.today() - timedelta(days=config["scraper"]["min_trading_days"])

    history = yf.download(symbol, period="max", interval="1d", progress=False)
    history = history[history.index > pd.to_datetime(start)]

    if len(history) == 0:
        return False

    # TODO: check Missing Close Price

    return True


def revive() -> None:
    target = abs_path(config["ignored_tickers"]["target"])
    df = pd.read_csv(target)

    revived = []

    with tqdm(total=len(df)) as progress:
        for symbol in df["Symbol"].values:
            ticker = yf.Ticker(symbol)

            if __is_ticker_alive(symbol, ticker):
                revived.append(symbol)

            progress.set_description(f"{symbol:>10}", refresh=False)
            progress.update(1)

    df = df[~df["Symbol"].isin(revived)]
    df.to_csv(target, index=False)
