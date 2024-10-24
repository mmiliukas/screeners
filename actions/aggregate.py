import datetime
import glob
import os.path

import pandas as pd
from tqdm import tqdm

from screeners.config import config
from screeners.download import download
from screeners.etfs import get_holdings, resolve_etf
from screeners.tickers import get_info, get_infos, get_tickers_whitelisted


def ignore(df: pd.DataFrame, reason: str) -> None:
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
        if screener["name"] in row and row[screener["name"]] > 0:
            names.append(screener["name"])
    return ",".join(names)


def enrich_close_date(row):
    symbol = row["Symbol"]

    end = row["Screener First Seen"]
    start = end - datetime.timedelta(days=14)

    file_name = f"first-seen/{symbol}.csv"

    if os.path.exists(file_name):
        history = pd.read_csv(file_name)
    else:
        history = download(symbol, start=start, end=end)
        history.to_csv(file_name)

    return pd.NA if len(history) == 0 else history.iloc[-1]["Close"]


def read_csv(file: str) -> pd.DataFrame:
    dates = ["Date"]
    date_format = "%Y-%m-%dT%H:%M:%S.%f"

    return pd.read_csv(file, parse_dates=dates, date_format=date_format)


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


def filter_out_with_zero_trading(tickers: list[str]) -> tuple[list[str], pd.DataFrame]:
    valid: list[str] = []
    invalid: list[str] = []

    days = config["scraper"]["min_trading_days"]
    start = datetime.date.today() - datetime.timedelta(days=days)

    with tqdm(total=len(tickers)) as progress:
        for ticker in tickers:
            df: pd.DataFrame = download(ticker, start=start)
            invalid.append(ticker) if df.empty else valid.append(ticker)
            progress.update(1)

    return (valid, pd.DataFrame({"Symbol": invalid}))


def aggregate() -> None:
    tickers = get_tickers_whitelisted()

    tickers, no_trading = filter_out_with_zero_trading(tickers)
    ignore(no_trading, "No Recent Trades")

    df = enrich_tickers(tickers)

    # 1. filter tickers only having sector (means categorized)
    filter_sector = ~df["Sector"].isna()
    ignore(df[~filter_sector], "Not Categorized")

    # 2. filter tickers where ratio is above threshold
    filter_ratio = df["Financials Current Ratio"] >= config["scraper"]["min_current_ratio"]
    ignore(df[~filter_ratio], "Current Ratio Below 0.5")

    # 3. calculate close price of the ticker before it was seen on a screener
    filter_by_close = ~df["Screener First Seen Close"].isna()
    ignore(df[~filter_by_close], "Missing Close Price")

    filter = filter_ratio & filter_sector & filter_by_close
    filtered = df[filter]

    filtered.to_csv(config["tickers"]["target"], index=False)

    df = enrich_tickers(get_holdings())
    df.to_csv(config["etf"]["target"], index=False)
