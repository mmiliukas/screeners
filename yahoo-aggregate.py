import datetime
import glob

import pandas as pd

from screeners.config import config
from screeners.etfs import get_holdings, resolve_etf
from screeners.tickers import get_info, get_infos, get_tickers_whitelisted


def ignore(df: pd.DataFrame, reason: str):
    if len(df) == 0:
        return

    now = datetime.datetime.now()
    ignored_target = config["ignored_tickers"]["target"]
    ignored = pd.read_csv(ignored_target, parse_dates=["Date"])

    for symbol in df["Symbol"].unique():
        ignored.loc[len(ignored.index)] = [symbol, now, reason]

    ignored.to_csv(ignored_target, index=False)


def enrich_screeners_names(row):
    names = []
    for screener in config["screeners"]:
        if row[screener["name"]] > 0:
            names.append(screener["name"])
    return ",".join(names)


def enrich_screeners(df: pd.DataFrame):
    for screener in config["screeners"]:
        csvs = glob.glob(f'{screener["cache_name"]}/*.csv')
        all = pd.concat([pd.read_csv(csv) for csv in csvs])
        df[screener["name"]] = df["Symbol"].apply(
            lambda _: len(all[all["Symbol"] == _])
        )

    df["Screener"] = df.apply(enrich_screeners_names, axis=1)


def enrich_tickers(symbols) -> pd.DataFrame:
    df = pd.DataFrame({"Symbol": symbols})

    df["Name"] = get_infos(df, ["longName", "shortName"])
    df["Sector"] = get_info(df, "sector")
    df["Industry"] = get_info(df, "industry")

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


def main():
    df = enrich_tickers(get_tickers_whitelisted())

    # custom filters to omit tickers in advance
    filter_sector = ~df["Sector"].isna()
    ignore(df[~filter_sector], "Not Categorized")

    filter_ratio = df["Financials Current Ratio"] >= 0.5
    ignore(df[~filter_ratio], "Current Ratio Below 0.5")

    filter = filter_ratio & filter_sector
    df[filter].to_csv(config["tickers"]["target"], index=False)

    df = enrich_tickers(get_holdings())
    df.to_csv(config["etf"]["target"], index=False)


if __name__ == "__main__":
    main()
