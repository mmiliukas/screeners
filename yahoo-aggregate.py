import yaml
import glob
import json
import pandas as pd

SECTOR_ETF = {
  'Basic Materials': 'XLB',
  'Financial Services': 'XLF',
  'Consumer Defensive': 'XLP',
  'Utilities': 'XLU',
  'Energy': 'XLE',
  'Technology': 'XLK',
  'Consumer Cyclical': 'XLY',
  'Real Estate': 'XLRE',
  'Healthcare': 'XLV',
  'Communication Services': 'XLC',
  'Industrials': 'XLI'
}

if __name__ == '__main__':
  with open('yahoo.yml', 'r') as file:
    config = yaml.safe_load(file)

  etfs = pd.read_csv('tickers-etf.csv')

  dfs = []
  for screener in config['screeners']:
    csvs = glob.glob(screener['cache'] + '*.csv')
    df = pd.concat([pd.read_csv(csv) for csv in csvs], ignore_index=True)
    df['Screener'] = screener['name']
    dfs.append(df)

  df = pd.concat(dfs, ignore_index=True)

  def resolve_sector(symbol):
    with open(config['tickers']['cache'] + symbol + '.json') as file:
      ticker = json.load(file)

    if len(ticker) > 0:
      return ticker[0]['sector'] if 'sector' in ticker[0] else ''

    return ''

  def resolve_industry(symbol):
    with open(config['tickers']['cache'] + symbol + '.json') as file:
      ticker = json.load(file)

    if len(ticker) > 0:
      return ticker[0]['industry'] if 'industry' in ticker[0] else ''

    return ''

  def resolve_etf(sector):
    return SECTOR_ETF[sector] if sector in SECTOR_ETF else ''

  df['Sector'] = df['Symbol'].apply(lambda x: resolve_sector(x))
  df['Industry'] = df['Symbol'].apply(lambda x: resolve_industry(x))
  df['ETF'] = df['Sector'].apply(lambda x: resolve_etf(x))

  df.to_csv(config['tickers']['target'], index=False)
