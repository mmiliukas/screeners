import json

import yfinance as yf

from screeners.cache import session
from screeners.config import config
from screeners.etfs import get_etfs
from screeners.tickers import get_tickers

if __name__ == "__main__":

    tickers = get_tickers()
    tickers.extend(get_etfs())

    for symbol in tickers:
        # TODO: maybe we should optimize and not refetch information each run
        result = yf.Ticker(symbol, session=session)

        ticker_path = config["tickers"]["cache_name"] + symbol + ".json"
        with open(ticker_path, "w") as file:
            file.write(json.dumps([result.info or {}]))
