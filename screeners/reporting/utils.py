import pandas as pd


def prefix(value: str, with_prefix: str) -> str:
    return value if not value else with_prefix + value


def diff_tickers(latest: pd.DataFrame, previous: pd.DataFrame) -> str:
    latest_symbols = set(latest["Symbol"].tolist())
    previous_symbols = set(previous["Symbol"].tolist())

    return ",".join(list(latest_symbols - previous_symbols))


def empty_zeros(x: int) -> str:
    return "" if x == 0 else "{0:+}".format(x)
