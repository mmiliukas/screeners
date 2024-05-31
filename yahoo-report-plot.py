#!/usr/bin/env python

import io
import logging
import logging.config
import sys

import matplotlib.gridspec as gs
import matplotlib.pyplot as plt
import yaml

from screeners.reporting.plot import (
    plot_etfs,
    plot_first_seen,
    plot_first_seen_by_screener,
    plot_ignored,
    plot_sector,
    plot_sum,
)
from screeners.reporting.read import read_ignored_tickers, read_tickers
from screeners.telegram import log_to_telegram_image

with open("config-logging.yml", "r") as config_logging:
    logging.config.dictConfig(yaml.safe_load(config_logging.read()))


def plot_to_buffer():
    graph = io.BytesIO()

    plt.tight_layout()
    plt.savefig(graph, format="png")

    graph.seek(0)
    return graph


def main(argv):
    bot_token, channel_id = argv[1:]

    tickers, previous_tickers = read_tickers()
    ignored_tickers, previous_ignored_tickers = read_ignored_tickers()

    fig = plt.figure(constrained_layout=True, figsize=(16, 8))
    grid = gs.GridSpec(1, 2, figure=fig)

    ax1 = fig.add_subplot(grid[0, 0])
    ax2 = fig.add_subplot(grid[0, 1])

    plot_sum(ax1, tickers)
    plot_sector(ax2, tickers)

    log_to_telegram_image(plot_to_buffer(), bot_token, channel_id)
    plt.close()

    fig = plt.figure(constrained_layout=True, figsize=(16, 8))
    grid = gs.GridSpec(2, 1, figure=fig)

    ax3 = fig.add_subplot(grid[0, 0])
    ax4 = fig.add_subplot(grid[1, 0])

    plot_first_seen(ax3, tickers)
    plot_ignored(ax3, ignored_tickers)
    plot_first_seen_by_screener(ax4, tickers)

    log_to_telegram_image(plot_to_buffer(), bot_token, channel_id)
    plt.close()

    fig = plt.figure(constrained_layout=True, figsize=(16, 8))
    grid = gs.GridSpec(1, 1, figure=fig)

    ax4 = fig.add_subplot(grid[0, 0])
    plot_etfs(ax4)

    log_to_telegram_image(plot_to_buffer(), bot_token, channel_id)
    plt.close()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
