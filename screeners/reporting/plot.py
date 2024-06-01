import json
from datetime import date

import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf

from screeners.config import config
from screeners.etfs import ETF_SECTOR, SECTOR_ETF

line_plot_params = {
    "kind": "line",
    "xlabel": "",
    "ylabel": "",
    "grid": True,
    "legend": True,
    "title": "Ticker appearance",
}


def plot_sum(ax, tickers: pd.DataFrame):
    names = [x["name"] for x in config["screeners"]]
    grouped = tickers[names].astype(bool).sum(axis=0).sort_values(ascending=False)
    grouped.plot(kind="barh", ax=ax, title="Tickers per screener (not unique)")
    ax.bar_label(ax.containers[0], fmt="%d", padding=10)


def plot_first_seen_by_screener(ax, tickers: pd.DataFrame):
    names = [x["name"] for x in config["screeners"]]
    dfs = []

    for name in names:
        filter_has_seen = ~tickers[f"{name} First Seen"].isna()
        filter_first_seen = (
            tickers[f"{name} First Seen"] == tickers["Screener First Seen"]
        )
        df = tickers[filter_has_seen & filter_first_seen].copy(deep=True)
        df["Date"] = pd.to_datetime(df[f"{name} First Seen"])
        df["Screener"] = name
        df["Count"] = 1
        dfs.append(df[["Date", "Screener", "Count"]])

    df = pd.concat(dfs)
    df = df.set_index("Date")

    df = df.groupby([pd.Grouper(freq="W-MON"), "Screener"]).sum().reset_index()
    df = df.pivot(index="Date", columns="Screener", values="Count").reset_index()

    df["Date"] = df["Date"].dt.date
    df.plot(kind="bar", stacked=True, colormap="tab20", ax=ax, x="Date", xlabel="")


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
                df.loc[len(df)] = [row["Sector"], row["Symbol"], name]  # type: ignore

    df = df.groupby(by=["Sector", "Screener"]).count()["Symbol"].unstack()  # type: ignore

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
    )  # type: ignore


def plot_etfs(ax):
    for ticker in SECTOR_ETF.values():
        df: pd.DataFrame = yf.download(
            ticker, period="1y", interval="1d", progress=False
        )
        label = label = ticker + " - " + ETF_SECTOR[ticker]
        df["Close"].plot(kind="line", ax=ax, label=label, legend=True, xlabel="")
    plt.xticks(rotation=0)


def read_json(name):
    with open(name, "r") as file:
        return json.load(file)


def plot_exchanges_by_screener(ax, tickers: pd.DataFrame):
    names = [x["name"] for x in config["screeners"]]

    filtered = tickers[["Exchange"] + names].copy(deep=True)
    filtered = filtered[filtered["Exchange"] == "PNK"]

    for name in names:
        filtered[name] = filtered[name].apply(lambda x: 1 if x > 0 else 0)

    stacked = filtered.set_index("Exchange").stack().to_frame("Count")  # type: ignore
    stacked = stacked.reset_index(names=["Exchange", "Screener"])

    grouped = stacked.groupby(["Screener", "Exchange"])["Count"].sum().unstack()
    grouped = grouped.sort_values("PNK", ascending=False)

    grouped.plot(kind="barh", ax=ax, title="PNK tickers per screener", xlabel="Count")
    ax.bar_label(ax.containers[0], fmt="%d", padding=10)


def plot_exchanges(ax, tickers: pd.DataFrame, ignored_tickers: pd.DataFrame):
    df1 = tickers[["Exchange"]].copy(deep=True)
    df1["Type"] = "Unique valid tickers"
    df1["Count"] = 1
    df1.fillna("MISSING", inplace=True)

    ignored = [read_json(f"tickers/{x}.json") for x in ignored_tickers["Symbol"].values]
    ignored = [x[0].get("exchange") for x in ignored]

    df2 = pd.DataFrame({"Exchange": ignored})
    df2["Type"] = "Ignored tickers"
    df2["Count"] = 1
    df2.fillna("MISSING", inplace=True)

    df = pd.concat([df1, df2])
    df = df.groupby(by=["Exchange", "Type"])["Count"].count().unstack()
    df.sort_values(by="Unique valid tickers", ascending=False, inplace=True)

    df.plot.barh(
        ax=ax,
        title="Yahoo exchanges",
        ylabel="Exchange",
        xlabel="Count",
        color=["tomato", "forestgreen"],
    )

    ax.bar_label(ax.containers[0], fmt="%d", padding=10)
    ax.bar_label(ax.containers[1], fmt="%d", padding=10)
