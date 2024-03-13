import sys

import pandas as pd

from screeners.config import config
from screeners.telegram import log_to_telegram


def main(argv):
    bot_token, channel_id = argv[1:]

    tickers = pd.read_csv(config["tickers"]["target"])
    ignored_tickers = pd.read_csv(config["ignored_tickers"]["target"])

    message = f"<b>DAILY RUN:</b> <code>{len(tickers)}</code> tickers matched and <code>{len(ignored_tickers)}</code> ignored"
    log_to_telegram(message, bot_token, channel_id)

    ignored_summary = ignored_tickers.groupby("Reason").count().to_string()
    log_to_telegram(f"<pre>{ignored_summary}</pre>", bot_token, channel_id)

    tickers_summary = tickers.groupby("Screener").count()["Symbol"].to_string()
    log_to_telegram(f"<pre>{tickers_summary}</pre>", bot_token, channel_id)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
