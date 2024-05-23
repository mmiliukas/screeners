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
import yfinance as yf

from screeners.config import config
from screeners.etfs import ETF_SECTOR, SECTOR_ETF
from screeners.telegram import log_to_telegram, log_to_telegram_image

with open("config-logging.yml", "r") as config_logging:
    logging.config.dictConfig(yaml.safe_load(config_logging.read()))


logger = logging.getLogger(__name__)

line_plot_params = {
    "kind": "line",
    "xlabel": "",
    "ylabel": "",
    "grid": True,
    "legend": True,
    "title": "Ticker appearance",
}


def read_tickers():
    source = config["tickers"]["target"]
    current = pd.read_csv(source, parse_dates=["Screener First Seen"])
    current["Screener First Seen"] = current["Screener First Seen"].dt.date

    source = "https://raw.githubusercontent.com/mmiliukas/screeners/main/" + source
    previous = pd.read_csv(source, parse_dates=["Screener First Seen"])
    previous["Screener First Seen"] = previous["Screener First Seen"].dt.date

    return (current, previous)


def read_ignored_tickers():
    source = config["ignored_tickers"]["target"]
    current = pd.read_csv(source, parse_dates=["Date"])
    current["Date"] = current["Date"].dt.date

    source = "https://raw.githubusercontent.com/mmiliukas/screeners/main/" + source
    previous = pd.read_csv(source, parse_dates=["Date"])
    previous["Date"] = previous["Date"].dt.date

    return (current, previous)


def plot_sum(ax, tickers: pd.DataFrame):
    names = [x["name"] for x in config["screeners"]]
    grouped = tickers[names].astype(bool).sum(axis=0).sort_values(ascending=False)
    grouped.plot(kind="barh", ax=ax, title="Tickers per screener (not unique)")
    ax.bar_label(ax.containers[0], fmt="%d", padding=10)


def plot_first_seen(ax, tickers: pd.DataFrame):
    count = tickers.groupby("Screener First Seen")["Symbol"].count()
    count.plot(label="New (excluding ignored)", ax=ax, **line_plot_params)

    moving_average = count.to_frame()["Symbol"].rolling(window=7).mean()
    moving_average.plot(label="Moving average (7 days)", ax=ax, **line_plot_params)


def plot_sector(ax, tickers: pd.DataFrame):
    names = [x["name"] for x in config["screeners"]]
    df = pd.DataFrame({"Sector": [], "Symbol": [], "Screener": []})

    for idx, row in tickers.iterrows():
        for name in names:
            if row[name] > 0:
                df.loc[len(df)] = [row["Sector"], row["Symbol"], name]

    df = df.groupby(by=["Sector", "Screener"]).count()["Symbol"].unstack()

    df.plot(
        kind="barh",
        ax=ax,
        colormap="tab20",
        ylabel="",
        stacked=True,
        title="Tickers per sector (not unique)",
    )


def plot_ignored(ax, ignored_tickers: pd.DataFrame):
    # at ????-??-13 we had a huge amount of removes, so ignoring them
    df = ignored_tickers[ignored_tickers["Date"] >= date.fromisoformat("2024-03-14")]
    df.groupby("Date")["Symbol"].count().plot(
        label="Ignored", ax=ax, **line_plot_params
    )


def summarize(tickers: pd.DataFrame, ignored_tickers: pd.DataFrame) -> str:
    return (
        f"<b>DAILY RUN:</b> {date.today().isoformat()}. "
        f"<code>{len(tickers)}</code> unique valid tickers + "
        f"<code>{len(ignored_tickers)}</code> ignored = "
        f"<code>{len(tickers) + len(ignored_tickers)}</code> total"
    )


def empty_zeros(x):
    return "" if x == 0 else "{0:+}".format(x)


def summarize_ignored(a: pd.DataFrame, b: pd.DataFrame) -> str:
    a = a.groupby("Reason")["Symbol"].count().to_frame()
    b = b.groupby("Reason")["Symbol"].count().to_frame()

    c = a - b
    c = c.rename(columns={"Symbol": "Delta"})

    result = a.join(c, how="outer")
    result["Delta"] = result["Delta"].apply(empty_zeros)
    result = result.sort_values(by="Symbol", ascending=False)

    return result.to_string(header=False, index_names=False)


def summarize_matched(a: pd.DataFrame, b: pd.DataFrame) -> str:
    names = [x["name"] for x in config["screeners"]]

    a = a[names].astype(bool).sum(axis=0).to_frame("Symbol")
    b = b[names].astype(bool).sum(axis=0).to_frame("Symbol")

    c = a - b
    c = c.rename(columns={"Symbol": "Delta"})

    result = a.join(c, how="outer")
    result["Delta"] = result["Delta"].apply(empty_zeros)
    result = result.sort_values(by="Symbol", ascending=False)

    return result.to_string(header=False, index_names=False)


def plot_etfs(ax):
    for ticker in SECTOR_ETF.values():
        df: pd.DataFrame = yf.download(ticker, period="1y", interval="1d")
        label = label = ticker + " - " + ETF_SECTOR[ticker]
        df["Close"].plot(kind="line", ax=ax, label=label, legend=True)
    plt.xticks(rotation=0)


def main(argv):
    bot_token, channel_id = argv[1:]

    tickers, previous_tickers = read_tickers()
    ignored_tickers, previous_ignored_tickers = read_ignored_tickers()

    message = summarize(tickers=tickers, ignored_tickers=ignored_tickers)
    log_to_telegram(message, bot_token, channel_id)

    message = summarize_ignored(ignored_tickers, previous_ignored_tickers)
    log_to_telegram(
        (
            f"Number of ignored tickers by reason.\n"
            f"<b>+/-</b> sign identifies increase/decrease from a previous run.\n\n"
            f"<code>{message}</code>"
        ),
        bot_token,
        channel_id,
    )

    message = summarize_matched(tickers, previous_tickers)
    log_to_telegram(
        (
            f"Number of tickers (excluding ignored) per screener.\n"
            f"Keep in mind that single ticker can appear in multiple screeners.\n"
            f"<b>+/-</b> sign identifies increase/decrease from a previous run.\n\n"
            f"<code>{message}</code>"
        ),
        bot_token,
        channel_id,
    )

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
