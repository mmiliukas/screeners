#!/usr/bin/env python

import io
import logging
import logging.config
import sys
from datetime import date

import matplotlib.gridspec as gs
import matplotlib.pyplot as plt
import pandas as pd
import yaml

from screeners.config import config
from screeners.reporting.plot import (
    plot_etfs,
    plot_first_seen,
    plot_ignored,
    plot_sector,
    plot_sum,
)
from screeners.reporting.read import read_ignored_tickers, read_tickers
from screeners.reporting.utils import diff_tickers, empty_zeros, prefix
from screeners.telegram import log_to_telegram, log_to_telegram_image

with open("config-logging.yml", "r") as config_logging:
    logging.config.dictConfig(yaml.safe_load(config_logging.read()))


faq = "https://github.com/mmiliukas/screeners/blob/main/FAQ.md"


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

    return df[["Metric", "Value", "Delta", "Added", "Removed"]].to_string(
        header=False, index=False, index_names=False
    )


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

    return result.to_string(header=False, index_names=False)


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

    return result.to_string(header=False, index_names=False)


def main(argv):
    bot_token, channel_id = argv[1:]

    message = f"<b>DAILY RUN:</b> {date.today().isoformat()} <a href='{faq}'>FAQ</a>"
    log_to_telegram(message, bot_token, channel_id)

    tickers, previous_tickers = read_tickers()
    ignored_tickers, previous_ignored_tickers = read_ignored_tickers()

    message = summarize(
        tickers,
        previous_tickers,
        ignored_tickers,
        previous_ignored_tickers,
    )
    log_to_telegram(f"<code>{message}</code>", bot_token, channel_id)

    message = summarize_ignored(ignored_tickers, previous_ignored_tickers)
    message = f"# of ignored tickers by reason \n\n<code>{message}</code>"
    log_to_telegram(message, bot_token, channel_id)

    message = summarize_matched(tickers, previous_tickers)
    message = f"# of tickers (excl. ignored) per screener\n\n<code>{message}</code>"
    log_to_telegram(message, bot_token, channel_id)

    fig = plt.figure(constrained_layout=True, figsize=(14, 10))
    grid = gs.GridSpec(2, 2, figure=fig)

    ax1 = fig.add_subplot(grid[0, 0])
    ax2 = fig.add_subplot(grid[0, 1])
    ax3 = fig.add_subplot(grid[1, :])

    plot_sum(ax1, tickers)
    plot_sector(ax2, tickers)
    plot_first_seen(ax3, tickers)
    plot_ignored(ax3, ignored_tickers)

    graph = io.BytesIO()
    plt.tight_layout()
    plt.savefig(graph, format="png")
    plt.close()
    log_to_telegram_image(graph.getbuffer(), bot_token, channel_id)

    fig = plt.figure(constrained_layout=True, figsize=(14, 10))
    grid = gs.GridSpec(1, 1, figure=fig)

    ax4 = fig.add_subplot(grid[0, 0])
    plot_etfs(ax4)

    graph = io.BytesIO()
    plt.tight_layout()
    plt.savefig(graph, format="png")
    log_to_telegram_image(graph.getbuffer(), bot_token, channel_id)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
