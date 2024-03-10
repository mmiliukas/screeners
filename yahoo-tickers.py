import json
import yfinance as yf

from screeners.config import config
from screeners.cache import session
from screeners.tickers import get_tickers, get_etfs

if __name__ == '__main__':

  tickers = get_tickers()
  tickers.extend(get_etfs())

  for symbol in tickers:

    result = yf.Ticker(symbol, session=session)

    ticker_path = config['tickers']['cache_name'] + symbol + '.json'
    with open(ticker_path, 'w') as file:
      file.write(json.dumps([result.info or {}]))

    ticker_balance_path = config['tickers']['balance_cache_name'] + symbol + '.csv'
    with open(ticker_balance_path, 'w') as file:
      result.get_balance_sheet(freq='quarterly').to_csv(ticker_balance_path, index=True) # type: ignore
