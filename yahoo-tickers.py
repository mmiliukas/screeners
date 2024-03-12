import json
import sys

import yfinance as yf

from screeners.cache import session
from screeners.config import config
from screeners.etfs import get_etfs_and_holdings
from screeners.tickers import get_tickers


def main():
    tickers = get_tickers()
    tickers.extend(get_etfs_and_holdings())

    for symbol in tickers:
        # TODO: maybe we should optimize and not refetch information each run
        # we could use file last modified time for that
        result = yf.Ticker(symbol, session=session)

        ticker_path = config["tickers"]["cache_name"] + symbol + ".json"
        with open(ticker_path, "w") as file:
            file.write(json.dumps([result.info or {}]))


if __name__ == "__main__":
    sys.exit(main())
