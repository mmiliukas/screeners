#!/usr/bin/env python

import logging
import logging.config
import sys
from datetime import date

import yaml

from screeners.reporting.read import read_ignored_tickers, read_tickers
from screeners.reporting.summarize import summarize
from screeners.reporting.summarize_ignored import summarize_ignored
from screeners.reporting.summarize_matched import summarize_matched
from screeners.telegram import log_to_telegram

with open("config-logging.yml", "r") as config_logging:
    logging.config.dictConfig(yaml.safe_load(config_logging.read()))


faq = "https://github.com/mmiliukas/screeners/blob/main/FAQ.md"


def main(argv):
    bot_token, channel_id, run_type = argv[1:]

    message = f"<b>{run_type}:</b> {date.today().isoformat()} <a href='{faq}'>FAQ</a>"
    log_to_telegram(message, bot_token, channel_id)

    tickers, previous_tickers = read_tickers()
    ignored_tickers, previous_ignored_tickers = read_ignored_tickers()

    message = summarize(
        tickers,
        previous_tickers,
        ignored_tickers,
        previous_ignored_tickers,
    )
    log_to_telegram(f"<code>{message}</code>", bot_token, channel_id)

    message = summarize_ignored(ignored_tickers, previous_ignored_tickers)
    message = f"# of ignored tickers by reason \n\n<code>{message}</code>"
    log_to_telegram(message, bot_token, channel_id)

    message = summarize_matched(tickers, previous_tickers)
    message = f"# of tickers (excl. ignored) per screener\n\n<code>{message}</code>"
    log_to_telegram(message, bot_token, channel_id)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
