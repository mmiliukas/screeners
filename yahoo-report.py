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


def main(argv):
    bot_token, channel_id = argv[1:]

    tickers = pd.read_csv(config["tickers"]["target"])
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

    screeners = __get_unique_screeners(tickers)
    only_screeners = tickers[screeners].astype(bool)
    ax = only_screeners.sum(axis=0).plot(kind="barh", figsize=(10, 3))
    ax.spines[
        [
            "top",
            "right",
        ]
    ].set_visible(False)
    ax.bar_label(ax.containers[0], fmt="%d", padding=10)  # type: ignore

    graph = io.BytesIO()
    plt.savefig(graph, format="png")

    log_to_telegram_image(graph.getbuffer(), bot_token, channel_id)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
