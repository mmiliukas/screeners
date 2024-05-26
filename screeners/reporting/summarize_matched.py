import pandas as pd

from screeners.config import config
from screeners.reporting.utils import diff_tickers, empty_zeros, prefix


def diff_tickers_matched(a: pd.DataFrame, b: pd.DataFrame, with_prefix: str):
    def filter_by_screener(screener: str):
        a_reason = a[a[screener] > 0]
        b_reason = b[b[screener] > 0]
        return prefix(diff_tickers(a_reason, b_reason), with_prefix)

    return filter_by_screener


def summarize_matched(aa: pd.DataFrame, bb: pd.DataFrame) -> str:
    names = [x["name"] for x in config["screeners"]]

    a = aa[names].astype(bool).sum(axis=0).to_frame("Symbol")
    b = bb[names].astype(bool).sum(axis=0).to_frame("Symbol")

    c = a - b
    c = c.rename(columns={"Symbol": "Delta"})

    result = a.join(c, how="outer")
    result["Delta"] = result["Delta"].apply(empty_zeros)
    result = result.sort_values(by="Symbol", ascending=False)

    result["Added"] = result.index
    result["Added"] = result["Added"].apply(diff_tickers_matched(aa, bb, "+"))

    result["Removed"] = result.index
    result["Removed"] = result["Removed"].apply(diff_tickers_matched(bb, aa, "-"))

    result["AddedRemoved"] = result["Added"] + result["Removed"]
    columns = ["Symbol", "Delta", "AddedRemoved"]

    return result[columns].to_string(header=False, index_names=False)
