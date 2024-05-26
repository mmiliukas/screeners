import pandas as pd

from screeners.reporting.utils import diff_tickers, empty_zeros, prefix


def summarize(
    tickers: pd.DataFrame,
    previous_tickers: pd.DataFrame,
    ignored_tickers: pd.DataFrame,
    previous_ignored_tickers: pd.DataFrame,
) -> str:
    df = pd.DataFrame(
        {
            "Metric": ["Unique valid tickers", "Ignored tickers", "Total"],
            "Value": [
                len(tickers),
                len(ignored_tickers),
                len(tickers) + len(ignored_tickers),
            ],
            "Previous Value": [
                len(previous_tickers),
                len(previous_ignored_tickers),
                len(previous_tickers) + len(previous_ignored_tickers),
            ],
            "Added": [
                prefix(diff_tickers(tickers, previous_tickers), "+"),
                prefix(diff_tickers(ignored_tickers, previous_ignored_tickers), "+"),
                "",
            ],
            "Removed": [
                prefix(diff_tickers(previous_tickers, tickers), "-"),
                prefix(diff_tickers(previous_ignored_tickers, ignored_tickers), "-"),
                "",
            ],
        }
    )

    df["Delta"] = df["Value"] - df["Previous Value"]
    df["Delta"] = df["Delta"].apply(empty_zeros)
    df["AddedRemoved"] = df["Added"] + df["Removed"]

    return df[["Metric", "Value", "Delta", "AddedRemoved"]].to_string(
        header=False, index=False, index_names=False
    )
