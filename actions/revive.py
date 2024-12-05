from datetime import date, timedelta
from time import sleep

import pandas as pd
import yfinance as yf
from tqdm import tqdm

from screeners.config import config
from screeners.download import download
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
    history = download(symbol, start=start, interval="1d")

    if len(history) == 0:
        return False

    # TODO: check Missing Close Price

    return True


def revive(reason: str) -> None:
    target = abs_path(config["ignored_tickers"]["target"])

    df = pd.read_csv(target)
    df_filtered = df[df["Reason"] == reason]

    revived = []

    with tqdm(total=len(df_filtered)) as progress:
        for symbol in df_filtered["Symbol"].values:

            ticker = yf.Ticker(symbol)

            if __is_ticker_alive(symbol, ticker):
                revived.append(symbol)

            progress.set_description(f"{symbol:>10}", refresh=False)
            progress.update(1)

            sleep(config["revive"]["sleep"])

    df = df[~df["Symbol"].isin(revived)]
    df.to_csv(target, index=False)
