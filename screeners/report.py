import json
from datetime import date, datetime, timedelta

import pandas as pd
import pandas_market_calendars as mcal
import yfinance as yf

from screeners.config import config
from screeners.etfs import ETF_SECTOR, SECTOR_ETF

screener_names = [screener["name"] for screener in config["screeners"]]


def read_json(name):
    try:
        with open(name, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return [{}]


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


def etfs_close() -> pd.DataFrame:
    tickers = ",".join(SECTOR_ETF.values())
    df = yf.download(tickers, period="1y", interval="1d", progress=False)
    result = df["Close"]
    result.index.name = "date"

    def rename_column(name: str) -> str:
        return f"{name} - {ETF_SECTOR[name]}"

    result.columns = [rename_column(col) for col in result.columns]
    return result


def tickers_by_sector(tickers: pd.DataFrame) -> pd.DataFrame:
    df = pd.DataFrame({"sector": [], "symbol": [], "screener": [], "group": []})

    for idx, row in tickers.iterrows():
        for name in screener_names:
            if row[name] > 0:
                df.loc[len(df)] = [
                    row["Sector"],
                    row["Symbol"],
                    name,
                    name.split(" ")[0],
                ]

    result = df.groupby(by=["sector", "group"]).count().reset_index()
    result = result.set_index("sector")
    result = result[["group", "symbol"]]
    result = result.pivot(columns="group", values="symbol")
    result = result.fillna(0)

    return result


def tickers_by_price(tickers: pd.DataFrame) -> pd.DataFrame:
    df = tickers[screener_names].astype(bool).sum(axis=0)
    df = df.to_frame("count").reset_index(names="screener")
    df["group"] = df["screener"].apply(lambda x: x.split(" ")[0])
    df["price_range"] = df["screener"].apply(lambda x: x.split(" ")[1])
    df.set_index("price_range", inplace=True)
    df = df.pivot(columns="group", values="count")

    return df


def tickers_by_screener(tickers: pd.DataFrame) -> pd.DataFrame:
    df = tickers[screener_names].astype(bool).sum(axis=0).sort_values(ascending=False)
    df = df.to_frame("count").reset_index(names="screener")
    df.set_index("screener", inplace=True)

    return df


def pnk_by_sector(tickers: pd.DataFrame) -> pd.DataFrame:
    df = tickers[tickers["Exchange"] == "PNK"]
    df = df.groupby(by=["Sector"])["Symbol"].count().to_frame()
    df = df.rename(columns={"Symbol": "symbol"})
    df.index.name = "sector"
    return df


def pnk_by_screener(tickers: pd.DataFrame) -> pd.DataFrame:
    df = tickers[tickers["Exchange"] == "PNK"]
    df = df[["Exchange"] + screener_names]

    for name in screener_names:
        df[name] = df[name].apply(lambda x: 1 if x > 0 else 0)

    df = df.set_index("Exchange").stack().to_frame("Count")  # type: ignore
    df = df.reset_index(names=["Exchange", "Screener"])

    df = df.groupby(["Screener", "Exchange"])["Count"].sum().unstack()
    df = df.rename(columns={"PNK": "count"})
    df.index.name = "screener"

    return df


def exchanges(tickers: pd.DataFrame, ignored_tickers: pd.DataFrame) -> pd.DataFrame:
    df1 = tickers[["Exchange"]].copy(deep=True)
    df1["type"] = "filtered"
    df1["count"] = 1
    df1.fillna("MISSING", inplace=True)

    ignored = [read_json(f"tickers/{x}.json") for x in ignored_tickers["Symbol"].values]
    ignored = [x[0].get("exchange") for x in ignored]

    df2 = pd.DataFrame({"Exchange": ignored})
    df2["type"] = "ignored"
    df2["count"] = 1
    df2.fillna("MISSING", inplace=True)

    df = pd.concat([df1, df2])
    df = df.groupby(by=["Exchange", "type"])["count"].count().unstack()
    df.index.name = "exchange"
    df.fillna(0, inplace=True)

    return df
