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
        f"<b>DAILY RUN: {date.today().isoformat()}</b> "
        f"<code>{len(tickers)}</code> matched + "
        f"<code>{len(ignored_tickers)}</code> ignored = "
        f"<code>{len(tickers) + len(ignored_tickers)}</code> total"
    )

    log_to_telegram(message, bot_token, channel_id)

    ignored_summary = (
        ignored_tickers.groupby("Reason")
        .count()["Symbol"]
        .sort_values(ascending=False)
        .to_string()
    )
    log_to_telegram(f"<pre>{ignored_summary}</pre>", bot_token, channel_id)

    tickers_summary = (
        tickers.groupby("Screener")
        .count()["Symbol"]
        .sort_values(ascending=False)
        .to_string()
    )
    log_to_telegram(f"<pre>{tickers_summary}</pre>", bot_token, channel_id)

    screeners = __get_unique_screeners(tickers)
    only_screeners = tickers[screeners]
    only_screeners.sum().plot(kind="pie", autopct=lambda p: "{:.2f}%".format(p))

    graph = io.BytesIO()
    plt.savefig(graph, format="png")

    log_to_telegram_image(graph, bot_token, channel_id)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
