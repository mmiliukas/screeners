#!/usr/bin/env python

import logging
import logging.config
import sys

import pandas as pd
import plotly.express as px
import yaml
from plotly.graph_objects import Figure

from screeners.config import config
from screeners.reporting.read import read_tickers

with open("config-logging.yml", "r") as config_logging:
    logging.captureWarnings(True)
    logging.config.dictConfig(yaml.safe_load(config_logging.read()))

screener_names = [screener["name"] for screener in config["screeners"]]


def tickers_frequency_bar(df: pd.DataFrame) -> Figure:
    grouped = df[screener_names].astype(bool).sum(axis=0).sort_values(ascending=False)
    grouped = grouped.to_frame("Count").reset_index(names="Screener")

    title = "Tickers per screener (not unique)"

    fig = px.bar(grouped, x="Screener", y="Count", text="Count", title=title)
    fig.update_traces(textposition="outside")

    return fig


def to_html(fig: Figure) -> str:
    return fig.to_html(full_html=False, include_plotlyjs=False)


def write_html(figs: list[Figure], filename: str) -> None:
    html = "\n".join([to_html(fig) for fig in figs])

    combined_html = f"""
<html>
<head>
    <title>Combined Plotly Figures</title>
    <script src="https://cdn.plot.ly/plotly-2.32.0.min.js" charset="utf-8"></script>
    <!-- <script src="https://cdn.plot.ly/plotly-latest.min.js"></script> -->
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

    fig = tickers_frequency_bar(tickers)
    write_html([fig], "./pages/index.html")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
