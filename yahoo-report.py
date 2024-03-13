import sys

import pandas as pd

from screeners.config import config
from screeners.telegram import log_to_telegram


def main(argv):
    bot_token, channel_id = argv[1:]

    tickers = len(pd.read_csv(config["tickers"]["target"]))
    ignore = len(pd.read_csv(config["ignored_tickers"]["target"]))

    message = f"<b>DAILY RUN:</b> <code>{tickers}</code> tickers matched and <code>{ignore}</code> ignored"
    log_to_telegram(message, bot_token, channel_id)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
