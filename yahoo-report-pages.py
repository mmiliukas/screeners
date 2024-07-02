#!/usr/bin/env python

import json
import logging
import logging.config
import sys
from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import plotly.io as pio
import yaml
import yfinance as yf
from matplotlib.pyplot import bar
from plotly.graph_objects import Figure

from screeners.config import config
from screeners.etfs import ETF_SECTOR, SECTOR_ETF
from screeners.reporting.read import read_ignored_tickers, read_tickers

with open("config-logging.yml", "r") as config_logging:
    logging.captureWarnings(True)
    logging.config.dictConfig(yaml.safe_load(config_logging.read()))

pio.templates.default = "plotly_white"

screener_names = [screener["name"] for screener in config["screeners"]]


def read_json(name):
    try:
        with open(name, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return [{}]


def days_ago(days: int) -> date:
    today = date.today()
    return today - timedelta(days=days)


def add_weekend_shapes(fig, dates):
    shapes = []
    for date in dates:
        if date.weekday() < 5:
            continue
        shapes.append(
            dict(
                type="rect",
                xref="x",
                yref="paper",
                x0=date + pd.Timedelta(days=-0.5),
                x1=date + pd.Timedelta(days=+0.5),
                y0=0,
                y1=1,
                fillcolor="rgba(0, 0, 0, 0.2)",
                line=dict(width=0),
                layer="below",
            )
        )
    return shapes


def first_seen(tickers: pd.DataFrame, ignored_tickers: pd.DataFrame) -> Figure:
    """
    Plot tickers by first seen date and include the ignored ones too.
    """

    max_age = days_ago(90)

    def group_first_seen(df: pd.DataFrame, column: str, name: str) -> pd.DataFrame:
        df = df[df[column] >= max_age]
        return df.groupby(column)["Symbol"].count().to_frame(name=name)

    a = group_first_seen(tickers, "Screener First Seen", "New")
    b = group_first_seen(ignored_tickers, "Date", "Ignored")

    b["Ignored"] = b["Ignored"] * -1
    c = a.join([b], how="outer")
    fig = px.bar(
        c,
        text="value",
        barmode="relative",
        title="Ticker appearance (last 30 days)",
        color_discrete_map={"New": "green", "Ignored": "red"},
    )

    ds = pd.date_range(start=c.index.min(), end=c.index.max())
    # fig.update_traces(showlegend=False)
    shapes = add_weekend_shapes(fig, ds)
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Count",
        shapes=shapes,
    )
    fig.update_xaxes(
        rangeselector=dict(
            buttons=list(
                [
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=2, label="2m", step="month", stepmode="backward"),
                    dict(step="all"),
                ]
            )
        )
    )

    return fig


def exchanges_by_sector(tickers: pd.DataFrame) -> Figure:
    filtered = tickers[["Exchange", "Sector"]].copy(deep=True)
    filtered = filtered[filtered["Exchange"] == "PNK"]
    filtered["Count"] = 1

    grouped = filtered.groupby(["Sector", "Exchange"])["Count"].sum().unstack()
    grouped = grouped.sort_values("PNK", ascending=False)

    params = {
        "data_frame": grouped,
        "height": 500,
        "barmode": "group",
        "title": "PNK per sector",
        "text": "value",
    }

    fig = px.bar(**params)
    fig.update_traces(textposition="outside")

    return fig


def exchanges_by_screener(tickers: pd.DataFrame) -> Figure:
    names = [x["name"] for x in config["screeners"]]

    filtered = tickers[["Exchange"] + names].copy(deep=True)
    filtered = filtered[filtered["Exchange"] == "PNK"]

    for name in names:
        filtered[name] = filtered[name].apply(lambda x: 1 if x > 0 else 0)

    stacked = filtered.set_index("Exchange").stack().to_frame("Count")  # type: ignore
    stacked = stacked.reset_index(names=["Exchange", "Screener"])

    grouped = stacked.groupby(["Screener", "Exchange"])["Count"].sum().unstack()
    grouped = grouped.sort_values("PNK", ascending=False)

    params = {
        "data_frame": grouped,
        "height": 500,
        "barmode": "group",
        "title": "PNK per screener",
        "text": "value",
    }

    fig = px.bar(**params)
    fig.update_traces(textposition="outside")

    return fig


def exchanges(tickers: pd.DataFrame, ignored_tickers: pd.DataFrame) -> Figure:
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

    params = {
        "data_frame": df,
        "height": 500,
        "barmode": "group",
        "title": "Yahoo exchanges",
        "text": "value",
    }

    fig = px.bar(**params)
    fig.update_traces(textposition="outside")

    return fig


def etfs() -> Figure:
    dfs = []
    for ticker in SECTOR_ETF.values():
        df = yf.download(ticker, period="3mo", interval="1d", progress=False)
        df["Symbol"] = " - ".join([ticker, ETF_SECTOR[ticker]])
        dfs.append(df)

    params = {
        "data_frame": pd.concat(dfs),
        "y": "Close",
        "color": "Symbol",
        "height": 500,
        "title": "ETF for the last 3 months",
    }

    return px.line(**params)


def tickers_by_sector(tickers: pd.DataFrame) -> Figure:
    df = pd.DataFrame({"Sector": [], "Symbol": [], "Screener": [], "Group": []})

    for idx, row in tickers.iterrows():
        for name in screener_names:
            if row[name] > 0:
                df.loc[len(df)] = [
                    row["Sector"],
                    row["Symbol"],
                    name,
                    name.split(" ")[0],
                ]

    result = df.groupby(by=["Sector", "Group"]).count().reset_index()  # type: ignore

    params = {
        "data_frame": result,
        "x": "Sector",
        "y": "Symbol",
        "color": "Group",
        "height": 500,
        "barmode": "stack",
        "title": "Ticker group (winner, random, looser) distribution per sector",
        "text": "Group",
    }

    fig = px.bar(**params)
    fig.update_traces(textposition="auto")
    return fig


def tickers_frequency(df: pd.DataFrame) -> Figure:
    grouped = df[screener_names].astype(bool).sum(axis=0).sort_values(ascending=False)
    grouped = grouped.to_frame("Count").reset_index(names="Screener")

    params = {
        "data_frame": grouped,
        "x": "Screener",
        "y": "Count",
        "text": "Count",
        "height": 500,
        "title": "Shows which screener finds the most tickers",
    }

    fig = px.bar(**params)
    fig.update_traces(textposition="auto", showlegend=False)

    return fig


def tickers_frequency_group(df: pd.DataFrame) -> Figure:
    grouped = df[screener_names].astype(bool).sum(axis=0).sort_values(ascending=False)
    grouped = grouped.to_frame("Count").reset_index(names="Screener")
    grouped["Group"] = grouped["Screener"].apply(lambda x: x.split(" ")[0])
    grouped["Price Range"] = grouped["Screener"].apply(lambda x: x.split(" ")[1])
    grouped["Price Range #"] = grouped["Screener"].apply(lambda x: int(x.split(" ")[1]))
    grouped.sort_values(by=["Price Range #", "Group"], inplace=True)

    params = {
        "data_frame": grouped,
        "x": "Price Range",
        "y": "Count",
        "color": "Group",
        "text": "Group",
        "height": 500,
        "barmode": "group",
        "title": "Shows number of found tickers distributed by price range and screener type",
    }

    fig = px.bar(**params)
    fig.update_traces(textposition="auto", showlegend=False)

    return fig


def to_html(fig: Figure) -> str:
    return fig.to_html(full_html=False, include_plotlyjs=False)


def write_html(figs: list[Figure], filename: str) -> None:
    html = "\n".join([to_html(fig) for fig in figs])

    combined_html = f"""
<!doctype html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Screeners</title>
    <script src="https://cdn.plot.ly/plotly-2.32.0.min.js" charset="utf-8"></script>
</head>
<body>
    {html}
</body>
</html>
"""

    with open(filename, "w") as file:
        file.write(combined_html)


def main(argv):
    tickers = read_tickers()[0]
    ignored_tickers = read_ignored_tickers()[0]

    figs = [
        first_seen(tickers, ignored_tickers),
        tickers_frequency(tickers),
        tickers_frequency_group(tickers),
        etfs(),
        tickers_by_sector(tickers),
        exchanges(tickers, ignored_tickers),
        exchanges_by_screener(tickers),
        exchanges_by_sector(tickers),
    ]

    write_html(figs, "./pages/index.html")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
