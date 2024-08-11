#!/usr/bin/env python

from datetime import date, timedelta
from typing import List

import pandas as pd
import yfinance as yf


def revive(df: pd.DataFrame) -> List[str]:
    revived = []

    for symbol in df["Symbol"].values:
        ticker = yf.Ticker(symbol)
        ticker_info = ticker.info

        if not ticker_info:
            # 404
            continue

        if ticker_info.get("symbol") != symbol:
            # 404
            continue

        if not ticker_info.get("sector"):
            # not categorized
            continue

        current_ratio = ticker_info.get("currentRatio") or 0
        if current_ratio < 0.5:
            # ratio below 0.5
            continue

        end = date.today()
        start = end - timedelta(days=14)

        history = yf.download(symbol, start=start, end=end, interval="1d")
        if len(history) == 0:
            # not being traded anymore, no trades in last 14 hours
            continue

        revived.append(symbol)

    return revived


if __name__ == "__main__":
    df = pd.read_csv("./tickers-ignored.csv")

    revived = revive(df)

    df = df[~df["Symbol"].isin(revived)]
    df.to_csv("./tickers-ignored.csv", index=False)
