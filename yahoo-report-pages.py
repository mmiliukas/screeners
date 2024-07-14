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
from plotly.graph_objects import Figure

from screeners.config import config
from screeners.reporting.read import read_tickers

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

    figs = [
        tickers_frequency(tickers),
        tickers_frequency_group(tickers),
    ]

    write_html(figs, "./pages/index.html")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
