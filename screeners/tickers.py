import glob
import json

import pandas as pd

from screeners.config import config


def get_tickers():
    runs = [screener["cache_name"] for screener in config["screeners"]]

    csvs = []
    for run in runs:
        csvs.extend(glob.glob(f"{run}/*.csv"))

    df = pd.concat([pd.read_csv(csv) for csv in csvs])

    return sorted(list(df["Symbol"].unique()))


def get_tickers_whitelisted():
    all = set(get_tickers())
    ignored = set(pd.read_csv(config["ignored_tickers"]["target"])["Symbol"].unique())

    return sorted(list(all - ignored))


def get_info(df: pd.DataFrame, key: str):
    def get_info_internal(row):
        file_name = config["tickers"]["cache_name"] + row + ".json"
        with open(file_name) as file:
            info = json.load(file)
            if len(info) == 0:
                return pd.NA
            return info[0][key] if key in info[0] else pd.NA

    return df["Symbol"].apply(get_info_internal)
