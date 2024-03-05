import yaml
import json
import os
import glob
import pandas as pd
import yfinance as yf

if __name__ == '__main__':
  with open('yahoo.yml', 'r') as file:
    config = yaml.safe_load(file)

  targets = [screener['target'] for screener in config['screeners']]

  runs = []
  for target in targets:
    runs.extend(glob.glob(f'{target}/*.csv'))

  df = pd.concat([pd.read_csv(csv) for csv in runs])

  tickers = list(df['Symbol'].unique())

  for ticker in tickers:
    path = config['tickers']['target'] + ticker + '.json'

    if not os.path.exists(path):
      print(f'fetching ticker, {ticker}...')

      result = yf.Ticker(ticker)
      with open(path, 'w') as f:
        f.write(json.dumps([result.info or {}]))
