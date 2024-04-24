#!/usr/bin/env python

import io
import logging
import logging.config
import sys
from datetime import date

import matplotlib.pyplot as plt
import pandas as pd
import yaml

from screeners.config import config
from screeners.telegram import log_to_telegram, log_to_telegram_image

with open("config-logging.yml", "r") as config_logging:
    logging.config.dictConfig(yaml.safe_load(config_logging.read()))


logger = logging.getLogger(__name__)


def __get_unique_screeners(df: pd.DataFrame):
    combined_screeners = df["Screener"].values
    result = set()
    for screeners in combined_screeners:
        for screener in screeners.split(","):
            result.add(screener)
    return list(result)


def __get_counts_by_screener(df: pd.DataFrame):
    by_screener = df[__get_unique_screeners(df)].astype(bool)
    by_screener = by_screener.sum(axis=0)
    by_screener = by_screener.sort_values(ascending=False)
    by_screener = by_screener.to_frame()
    by_screener = by_screener.rename(columns={0: "total"})
    return by_screener


def __log_diff(df1: pd.DataFrame, df2: pd.DataFrame, bot_token: str, channel_id: str):
    summary = df1.join(df1 - df2, how="outer", lsuffix=" now", rsuffix=" diff")
    summary = summary.to_string()
    log_to_telegram(f"<pre>{summary}</pre>", bot_token, channel_id)


def __plot_ticker_count_per_screener(axis, tickers: pd.DataFrame):
    screeners = __get_unique_screeners(tickers)
    only_screeners = tickers[screeners].astype(bool)
    ax = (
        only_screeners.sum(axis=0)
        .sort_values(ascending=False)
        .plot(kind="barh", ax=axis)
    )
    ax.spines[["top", "right"]].set_visible(False)
    ax.bar_label(ax.containers[0], fmt="%d", padding=10)  # type: ignore


def __plot_ticker_frequency(axis, tickers: pd.DataFrame):
    tickers["SFS"] = tickers["Screener First Seen"].dt.date
    ax = (
        tickers.groupby("SFS")["Symbol"]
        .count()
        .plot(
            kind="line",
            ax=axis,
            xlabel="",
            ylabel="",
            grid=True,
            legend=True,
            label="Matched",
        )
    )
    ax.spines[["top", "right"]].set_visible(False)

    moving_average = tickers.groupby("SFS")["Symbol"].count().to_frame()
    moving_average["ma"] = moving_average["Symbol"].rolling(window=7).mean()
    moving_average["ma"].plot(
        kind="line",
        ax=axis,
        grid=True,
        legend=True,
        label="Moving average (7 days)",
        xlabel="",
        ylabel="",
    )


def __plot_ignored_tickers(axis):
    df = pd.read_csv(config["ignored_tickers"]["target"], parse_dates=["Date"])
    df["Date"] = df["Date"].dt.date

    # at ????-??-13 we had a huge amount of removes, so ignoring them
    df = df[df["Date"] >= date.fromisoformat("2024-03-14")]
    df.groupby("Date")["Symbol"].count().plot(
        kind="line",
        ax=axis,
        legend=True,
        grid=True,
        label="Ignored",
        xlabel="",
        ylabel="",
    )


def main(argv):
    bot_token, channel_id = argv[1:]

    tickers_source = config["tickers"]["target"]
    tickers = pd.read_csv(tickers_source, parse_dates=["Screener First Seen"])

    previous = "https://raw.githubusercontent.com/mmiliukas/screeners/main/"
    previous_source = previous + tickers_source
    previous_tickers = pd.read_csv(previous_source, parse_dates=["Screener First Seen"])

    ignored_source = config["ignored_tickers"]["target"]
    ignored_tickers = pd.read_csv(ignored_source)
    previous_ignored_tickers = pd.read_csv(previous + ignored_source)

    message = (
        f"<b>DAILY RUN:</b> {date.today().isoformat()}\n"
        f"<code>{len(tickers)}</code> matched + "
        f"<code>{len(ignored_tickers)}</code> ignored = "
        f"<code>{len(tickers) + len(ignored_tickers)}</code> total"
    )

    log_to_telegram(message, bot_token, channel_id)

    # output ignored ticker stats
    df1 = ignored_tickers.groupby("Reason")["Symbol"].count().to_frame()
    df2 = previous_ignored_tickers.groupby("Reason")["Symbol"].count().to_frame()
    __log_diff(df1, df2, bot_token, channel_id)

    # output screener counts and their diff from previous run
    df1 = __get_counts_by_screener(tickers)
    df2 = __get_counts_by_screener(previous_tickers)
    __log_diff(df1, df2, bot_token, channel_id)

    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(14, 10))

    __plot_ticker_count_per_screener(axes[0], tickers)
    __plot_ticker_frequency(axes[1], tickers)
    __plot_ignored_tickers(axes[1])

    plt.tight_layout()

    graph = io.BytesIO()
    plt.savefig(graph, format="png")

    log_to_telegram_image(graph.getbuffer(), bot_token, channel_id)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
