import datetime
import json
import logging
import logging.config
import os.path
import sys

import pandas as pd
import yaml
import yfinance as yf

from screeners.cache import session
from screeners.config import config
from screeners.etfs import get_etfs_and_holdings
from screeners.tickers import get_tickers

with open("config-logging.yml", "r") as config_logging:
    logging.config.dictConfig(yaml.safe_load(config_logging.read()))

logger = logging.getLogger(__name__)


def should_update(df: pd.DataFrame, symbol: str, ticker_file: str):
    if len(df[df["Symbol"] == symbol]) > 0:
        # ticker is ignored, no need to update
        return False

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

    ignored_tickers = config["ignored_tickers"]["target"]
    df = pd.read_csv(ignored_tickers, parse_dates=["Date"])

    for symbol in tickers:
        ticker_path = config["tickers"]["cache_name"] + symbol + ".json"

        if should_update(df, symbol, ticker_path):
            result = yf.Ticker(symbol, session=session)
            if not result.info or "symbol" not in result.info:
                logger.info(f'ticker "{symbol}" not found on yahoo.com, ignoring...')

                now = datetime.datetime.now()
                df.loc[len(df.index)] = [symbol, now, "Not Found"]
            else:
                logger.info(f'refreshing ticker "{symbol}" information...')

                with open(ticker_path, "w") as file:
                    file.write(json.dumps([result.info or {}]))

    df.to_csv(ignored_tickers, index=False)


if __name__ == "__main__":
    sys.exit(main())
