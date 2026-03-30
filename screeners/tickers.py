import glob
import json

import pandas as pd

from screeners.config import config


def get_tickers() -> list[str]:
    runs = [screener["cache_name"] for screener in config["screeners"]]

    csvs = []
    for run in runs:
        csvs.extend(glob.glob(f"{run}/*.csv"))

    all_df = [pd.read_csv(csv) for csv in csvs]
    all_df = list(filter(lambda x: not x.empty, all_df))
    df = pd.concat(all_df)

    return sorted(list(df["Symbol"].unique()))


def get_tickers_whitelisted():
    all = set(get_tickers())
    ignored = set(pd.read_csv(config["ignored_tickers"]["target"])["Symbol"].unique())

    return sorted(list(all - ignored))


def get_infos(df: pd.DataFrame, keys: list[str]):
    def get_info_internal(row):
        file_name = config["tickers"]["cache_name"] + row + ".json"
        with open(file_name) as file:
            info = json.load(file)

            if len(info) == 0:
                return pd.NA

            for key in keys:
                value = info[0][key] if key in info[0] else None
                if value is not None:
                    return value

            return pd.NA

    return df["Symbol"].apply(get_info_internal)


def get_info(df: pd.DataFrame, key: str):
    return get_infos(df, [key])
