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

PREVIOUS_SOURCE = "https://raw.githubusercontent.com/mmiliukas/screeners/main/"


def __get_unique_screeners(df: pd.DataFrame):
    combined_screeners = df["Screener"].values
    result = set()
    for screeners in combined_screeners:
        for screener in screeners.split(","):
            result.add(screener)
    return list(result)


def __get_counts_by_screener(df: pd.DataFrame):
    by_screener = df[__get_unique_screeners(df)].astype(bool)
    by_screener = by_screener.sum(axis=0).to_frame()
    return by_screener


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


def read_tickers():
    source = config["tickers"]["target"]
    current = pd.read_csv(source, parse_dates=["Screener First Seen"])

    source = "https://raw.githubusercontent.com/mmiliukas/screeners/main/" + source
    previous = pd.read_csv(source, parse_dates=["Screener First Seen"])

    return (current, previous)


def read_ignored_tickers():
    source = config["ignored_tickers"]["target"]
    current = pd.read_csv(source)

    source = "https://raw.githubusercontent.com/mmiliukas/screeners/main/" + source
    previous = pd.read_csv(source)

    return (current, previous)


def main(argv):
    bot_token, channel_id = argv[1:]

    tickers, previous_tickers = read_tickers()
    ignored_tickers, previous_ignored_tickers = read_ignored_tickers()

    # log first line (summary of matched + ignored = total)
    message = (
        f"<b>DAILY RUN:</b> {date.today().isoformat()}\n"
        f"<code>{len(tickers)}</code> matched + "
        f"<code>{len(ignored_tickers)}</code> ignored = "
        f"<code>{len(tickers) + len(ignored_tickers)}</code> total"
    )
    log_to_telegram(message, bot_token, channel_id)

    # output ignored ticker stats
    a = ignored_tickers.groupby("Reason")["Symbol"].count().to_frame()
    b = previous_ignored_tickers.groupby("Reason")["Symbol"].count().to_frame()
    c = a.join(a - b, how="outer", lsuffix="_a", rsuffix="_b")
    c["c"] = c["Symbol_b"].apply(lambda x: "" if x == 0 else "{0:+}".format(x))
    d = c[["Symbol_a", "c"]].to_string(header=False, index_names=False)
    log_to_telegram(f"<code>{d}</code>", bot_token, channel_id)

    # output screener stats
    a = __get_counts_by_screener(tickers)
    b = __get_counts_by_screener(previous_tickers)
    c = a.join(a - b, how="outer", lsuffix="_a", rsuffix="_b")
    c["c"] = c["0_b"].apply(lambda x: "" if x == 0 else "{0:+}".format(x))
    d = c[["0_a", "c"]].to_string(header=False, index_names=False)
    log_to_telegram(f"<code>{d}</code>", bot_token, channel_id)

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
