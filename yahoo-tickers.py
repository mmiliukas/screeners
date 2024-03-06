import yaml
import json
import os
import glob
import pandas as pd
import yfinance as yf
from datetime import timedelta
from requests_cache import CachedSession

# https://requests-cache.readthedocs.io/en/stable/user_guide.html
cache_session = CachedSession('.cache-yfinance',
                              backend='filesystem',
                              expire_after=timedelta(days=5))

if __name__ == '__main__':
  with open('yahoo.yml', 'r') as file:
    config = yaml.safe_load(file)

  targets = [screener['cache'] for screener in config['screeners']]

  runs = []
  for target in targets:
    runs.extend(glob.glob(f'{target}/*.csv'))

  df = pd.concat([pd.read_csv(csv) for csv in runs])

  tickers = list(df['Symbol'].unique())

  for i, ticker in enumerate(tickers):
    print(i, '/', len(tickers))
    path = config['tickers']['cache'] + ticker + '.json'

    #if not os.path.exists(path):
    #  print(f'fetching ticker, {ticker}...')

    result = yf.Ticker(ticker, session=cache_session)

    with open(path, 'w') as f:
      f.write(json.dumps([result.info or {}]))
