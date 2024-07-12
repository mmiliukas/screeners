#!/usr/bin/env python

from datetime import date, datetime, timedelta

import pandas as pd
import pandas_market_calendars as mcal
import yfinance as yf

from screeners.etfs import ETF_SECTOR, SECTOR_ETF
from screeners.reporting.read import read_ignored_tickers, read_tickers


def date_to_timestamp(value: date) -> int:
    midnight = datetime.combine(value, datetime.min.time())
    return int(midnight.timestamp() * 1_000)


def calendar() -> pd.DataFrame:
    start_date = date.today() - timedelta(days=365)
    end_date = date.today() + timedelta(days=365)

    nyse = mcal.get_calendar("NYSE")
    schedule = nyse.schedule(start_date=start_date, end_date=end_date)

    range = pd.date_range(start=start_date, end=end_date, freq="D")

    df = pd.DataFrame(index=range)
    df.index.name = "date"

    df["date_timestamp"] = df.index.to_series().apply(date_to_timestamp)
    df["is_weekend"] = df.index.to_series().apply(lambda x: x.weekday() >= 5)
    df["is_holiday"] = ~df["is_weekend"] & ~df.index.isin(schedule.index)
    df["is_non_working_day"] = df["is_weekend"] | df["is_holiday"]

    return df


def first_seen(tickers: pd.DataFrame, ignored_tickers: pd.DataFrame) -> pd.DataFrame:

    def concat(series, separator=", ") -> str:
        return separator.join(series)

    def group(df: pd.DataFrame, column: str, name: str) -> pd.DataFrame:
        params = {}
        params[name] = ("Symbol", "count")
        params[f"{name}_tickers"] = ("Symbol", concat)
        return df.groupby(column).agg(**params)

    a = group(tickers, "Screener First Seen", "new")
    b = group(ignored_tickers, "Date", "ignored")

    b["ignored"] = -b["ignored"]

    c = a.join([b], how="outer")

    full_date_range = pd.date_range(start=c.index.min(), end=c.index.max())

    c = c.reindex(full_date_range)
    c.index.name = "date"

    c["ignored"] = c["ignored"].fillna(0).astype(int)
    c["new"] = c["new"].fillna(0).astype(int)
    c["ignored_tickers"] = c["ignored_tickers"].fillna("").astype(str)
    c["new_tickers"] = c["new_tickers"].fillna("").astype(str)

    c["date_timestamp"] = c.index.to_series().apply(date_to_timestamp)

    return c


def etfs() -> pd.DataFrame:
    dfs = []
    for ticker in SECTOR_ETF.values():
        df = yf.download(ticker, period="1y", interval="1d", progress=False)
        df["Symbol"] = ticker
        df["Sector"] = ETF_SECTOR[ticker]
        dfs.append(df[["Close", "Volume", "Symbol", "Sector"]])
    result = pd.concat(dfs)
    result.index.name = "date"
    result = result.rename(
        columns={
            "Close": "close",
            "Volume": "volume",
            "Symbol": "symbol",
            "Sector": "sector",
        }
    )
    return result


def main() -> None:
    tickers = read_tickers()
    ignored_tickers = read_ignored_tickers()

    df = calendar()
    df.to_csv("./reports/calendar.csv", float_format="%.0f")

    df = first_seen(tickers[0], ignored_tickers[0])
    df.to_csv("./reports/first-seen.csv", float_format="%.0f")

    df = etfs()
    df.to_csv("./reports/etfs.csv", float_format="%.2f")


if __name__ == "__main__":
    main()
