import datetime
import json
import os.path
import sys

import yfinance as yf

from screeners.cache import session
from screeners.config import config
from screeners.etfs import get_etfs_and_holdings
from screeners.tickers import get_tickers


def should_update(ticker_file):
    expire_after_days = config["yfinance"]["expire_after_days"]
    if os.path.exists(ticker_file):
        modified_at = os.path.getmtime(ticker_file)
        modified_at_date = datetime.datetime.fromtimestamp(modified_at)
        diff = datetime.datetime.now() - modified_at_date
        return True if diff.days >= expire_after_days else False
    return True


def main():
    tickers = get_tickers()
    tickers.extend(get_etfs_and_holdings())

    for symbol in tickers:
        ticker_path = config["tickers"]["cache_name"] + symbol + ".json"

        if should_update(ticker_path):
            result = yf.Ticker(symbol, session=session)
            with open(ticker_path, "w") as file:
                # TODO: update ignored tickers file if no results are returned
                file.write(json.dumps([result.info or {}]))


if __name__ == "__main__":
    sys.exit(main())
