import sys
from datetime import date

import pandas as pd

from screeners.config import config
from screeners.telegram import log_to_telegram


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


if __name__ == "__main__":
    sys.exit(main(sys.argv))
