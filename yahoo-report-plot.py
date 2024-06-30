#!/usr/bin/env python

import io
import logging
import logging.config
import sys

import matplotlib.gridspec as gs
import matplotlib.pyplot as plt
import yaml

from screeners.reporting.plot import (
    plot_first_seen,
    plot_first_seen_by_screener,
    plot_ignored,
)
from screeners.reporting.read import read_ignored_tickers, read_tickers
from screeners.telegram import log_to_telegram_image

with open("config-logging.yml", "r") as config_logging:
    logging.captureWarnings(True)
    logging.config.dictConfig(yaml.safe_load(config_logging.read()))


def plot_grid(
    figsize: tuple[float, float] = (16, 8),
    rows: int = 1,
    cols: int = 1,
    subplots: list[tuple[int, int]] = [(0, 0)],
):
    fig = plt.figure(constrained_layout=True, figsize=figsize)
    grid = gs.GridSpec(rows, cols, figure=fig)

    return [fig.add_subplot(grid[x[0], x[1]]) for x in subplots]


def plot_to_buffer():
    graph = io.BytesIO()

    plt.tight_layout()
    plt.show()
    plt.savefig(graph, format="png")
    plt.close()

    graph.seek(0)
    return graph


def main(argv):
    bot_token, channel_id = argv[1:]

    tickers = read_tickers()[0]
    ignored_tickers = read_ignored_tickers()[0]

    ax1, ax2 = plot_grid(rows=2, cols=1, subplots=[(0, 0), (1, 0)])
    plot_first_seen(ax1, tickers)
    plot_ignored(ax1, ignored_tickers)
    plot_first_seen_by_screener(ax2, tickers)
    log_to_telegram_image(plot_to_buffer(), bot_token, channel_id)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
