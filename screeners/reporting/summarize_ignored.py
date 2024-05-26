import pandas as pd

from screeners.reporting.utils import diff_tickers, empty_zeros, prefix


def diff_tickers_ignored(a: pd.DataFrame, b: pd.DataFrame, with_prefix: str):
    def filter_by_reason(reason: str):
        a_reason = a[a["Reason"] == reason]
        b_reason = b[b["Reason"] == reason]
        return prefix(diff_tickers(a_reason, b_reason), with_prefix)

    return filter_by_reason


def summarize_ignored(aa: pd.DataFrame, bb: pd.DataFrame) -> str:
    a = aa.groupby("Reason")["Symbol"].count().to_frame()
    b = bb.groupby("Reason")["Symbol"].count().to_frame()

    c = a - b
    c = c.rename(columns={"Symbol": "Delta"})

    result = a.join(c, how="outer")
    result["Delta"] = result["Delta"].apply(empty_zeros)
    result = result.sort_values(by="Symbol", ascending=False)

    result["Added"] = result.index
    result["Added"] = result["Added"].apply(diff_tickers_ignored(aa, bb, "+"))

    result["Removed"] = result.index
    result["Removed"] = result["Removed"].apply(diff_tickers_ignored(bb, aa, "-"))

    result["AddedRemoved"] = result["Added"] + result["Removed"]

    columns = ["Symbol", "Delta", "AddedRemoved"]
    return result[columns].to_string(header=False, index_names=False)
