import glob

import pandas as pd

from screeners.config import config
from screeners.etfs import resolve_etf
from screeners.tickers import get_info, get_infos, get_tickers_whitelisted


def enrich_screeners_names(row):
    names = []
    for screener in config["screeners"]:
        if screener["name"] in row and row[screener["name"]] > 0:
            names.append(screener["name"])
    return ",".join(names)


def enrich_close_date(row):
    symbol = row["Symbol"]

    file_name = f"first-seen/{symbol}.csv"
    history = pd.read_csv(file_name)

    return history.iloc[-1]["Close"]


def read_csv(file: str) -> pd.DataFrame:
    return pd.read_csv(file, parse_dates=["Date"], date_format="%Y-%m-%dT%H:%M:%S.%f")


def exclude_empty(dfs: list[pd.DataFrame]) -> list[pd.DataFrame]:
    return list(filter(lambda x: not x.empty, dfs))


def enrich_screeners(df: pd.DataFrame):
    for screener in config["screeners"]:
        csvs = glob.glob(f'{screener["cache_name"]}/*.csv')
        all = exclude_empty([read_csv(csv) for csv in csvs])

        if len(all) == 0:
            df[screener["name"]] = 0
            df[screener["name"] + " First Seen"] = pd.NaT
            continue

        all = pd.concat(all)

        df[screener["name"]] = df["Symbol"].apply(lambda _: len(all[all["Symbol"] == _]))  # type: ignore

        df[screener["name"] + " First Seen"] = df["Symbol"].apply(
            lambda _: all[all["Symbol"] == _]["Date"].min()  # type: ignore
        )

    df["Screener"] = df.apply(enrich_screeners_names, axis=1)

    # create a derived column which tells the max occurance
    names = list(map(lambda screener: screener["name"], config["screeners"]))
    df["Screener Max"] = df[names].idxmax(axis=1)

    names = [screener["name"] + " First Seen" for screener in config["screeners"]]
    df["Screener First Seen"] = df[names].min(axis=1)
    df["Screener First Seen Close"] = df.apply(enrich_close_date, axis=1)


def enrich_tickers(symbols) -> pd.DataFrame:
    df = pd.DataFrame({"Symbol": symbols})

    df["Name"] = get_infos(df, ["longName", "shortName"])
    df["Sector"] = get_info(df, "sector")
    df["Industry"] = get_info(df, "industry")
    df["Exchange"] = get_info(df, "exchange")

    df["ETF"] = df["Sector"].apply(resolve_etf)

    enrich_screeners(df)

    df["Financials Market Cap"] = get_info(df, "marketCap")
    df["Financials Total Cash"] = get_info(df, "totalCash")
    df["Financials Total Debt"] = get_info(df, "totalDebt")
    df["Financials Quick Ratio"] = get_info(df, "quickRatio")
    df["Financials Current Ratio"] = get_info(df, "currentRatio")
    df["Financials Total Revenue"] = get_info(df, "totalRevenue")
    df["Financials Debt To Equity"] = get_info(df, "debtToEquity")
    df["Financials Return On Assets"] = get_info(df, "returnOnAssets")
    df["Financials Return On Equity"] = get_info(df, "returnOnEquity")
    df["Financials Free Cashflow"] = get_info(df, "freeCashflow")
    df["Financials Operating Cashflow"] = get_info(df, "operatingCashflow")

    return df


def aggregate() -> None:
    tickers = get_tickers_whitelisted()

    df = enrich_tickers(tickers)
    df.to_csv(config.tickers.target, index=False)
