import glob

import pandas as pd

from screeners.config import config


def mark_as_ignored(df: pd.DataFrame):
    a = set(df["Symbol"].unique())
    b = set(pd.read_csv("./tickers-ignored.csv")["Symbol"].unique())
    c = sorted(list(a | b))

    df = pd.DataFrame({"Symbol": c})
    df.to_csv("./tickers-ignored.csv", index=False)


def get_tickers():
    runs = [screener["cache_name"] for screener in config["screeners"]]

    csvs = []
    for run in runs:
        csvs.extend(glob.glob(f"{run}/*.csv"))

    df = pd.concat([pd.read_csv(csv) for csv in csvs])

    all = set(df["Symbol"].unique())
    ignore = set(pd.read_csv("./tickers-ignored.csv")["Symbol"].unique())

    return sorted(list(all - ignore))
