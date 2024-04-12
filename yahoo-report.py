#!/usr/bin/env python

import io
import sys
from datetime import date

import matplotlib.pyplot as plt
import pandas as pd

from screeners.config import config
from screeners.telegram import log_to_telegram, log_to_telegram_image


def __get_unique_screeners(df: pd.DataFrame):
    combined_screeners = df["Screener"].values
    result = set()
    for screeners in combined_screeners:
        for screener in screeners.split(","):
            result.add(screener)
    return list(result)


def __plot_ticker_count_per_screener(axis, tickers: pd.DataFrame):
    axis.set_title("Tickers per screener")

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
    axis.set_title("Ticker appearance frequency")

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
            label="Count",
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

    ignored_tickers = pd.read_csv(config["ignored_tickers"]["target"])

    message = (
        f"<b>DAILY RUN:</b> {date.today().isoformat()}\n"
        f"<code>{len(tickers)}</code> matched + "
        f"<code>{len(ignored_tickers)}</code> ignored = "
        f"<code>{len(tickers) + len(ignored_tickers)}</code> total"
    )

    log_to_telegram(message, bot_token, channel_id)

    ignored_summary = (
        ignored_tickers.groupby("Reason")
        .count()["Symbol"]
        .sort_values(ascending=False)
        .to_string(header=False)
    )
    log_to_telegram(f"<pre>{ignored_summary}</pre>", bot_token, channel_id)

    tickers_summary = (
        tickers.groupby("Screener")
        .count()["Symbol"]
        .sort_values(ascending=False)
        .to_string(header=False)
    )
    log_to_telegram(f"<pre>{tickers_summary}</pre>", bot_token, channel_id)

    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(10, 7))

    __plot_ticker_count_per_screener(axes[0], tickers)
    __plot_ticker_frequency(axes[1], tickers)
    __plot_ignored_tickers(axes[1])

    plt.tight_layout()

    graph = io.BytesIO()
    plt.savefig(graph, format="png")

    log_to_telegram_image(graph.getbuffer(), bot_token, channel_id)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
