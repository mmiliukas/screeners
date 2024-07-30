import os
from typing import List

import pandas as pd
import yfinance as yf

from screeners.utils import progress


def read_history(file_name: str) -> pd.DataFrame:
    return pd.read_csv(file_name, parse_dates=["Date"], index_col="Date")


def download_history(tickers: List[str], period: str, to: str) -> None:
    os.makedirs(to, exist_ok=True)

    for index, ticker in enumerate(tickers):
        progress("downloading the history", index + 1, len(tickers))

        file_name = os.path.join(to, f"{ticker}.csv")
        history = yf.download(ticker, period=period, interval="1d", progress=False)
        history.to_csv(file_name)
