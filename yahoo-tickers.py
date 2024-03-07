import json
import glob
import pandas as pd
import yfinance as yf

from screeners.config import config
from screeners.cache import session

if __name__ == '__main__':

  runs = [screener['cache_name'] for screener in config['screeners']]

  csvs = []
  for run in runs: csvs.extend(glob.glob(f'{run}/*.csv'))

  df = pd.concat([pd.read_csv(csv) for csv in csvs])

  for symbol in df['Symbol'].unique():

    result = yf.Ticker(symbol, session=session)

    ticker_path = config['tickers']['cache_name'] + symbol + '.json'
    with open(ticker_path, 'w') as file:
      file.write(json.dumps([result.info or {}]))

    ticker_balance_path = config['tickers']['balance_cache_name'] + symbol + '.csv'
    with open(ticker_balance_path, 'w') as file:
      result.get_balance_sheet(freq='quarterly').to_csv(ticker_balance_path, index=True) # type: ignore
