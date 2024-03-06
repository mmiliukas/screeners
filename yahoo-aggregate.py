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

  json_cache = {}

  def read_value_from_json(symbol: str, key: str, default = None):
    if symbol not in json_cache:
      with open(config['tickers']['cache'] + symbol + '.json') as file:
        json_cache[symbol] = json.load(file)
    ticker = json_cache[symbol]
    if len(ticker) == 0:
      return default
    return ticker[0][key] if key in ticker[0] else default

  etfs = pd.read_csv('tickers-etf.csv')

  dfs = []
  for screener in config['screeners']:
    csvs = glob.glob(screener['cache'] + '*.csv')
    df = pd.concat([pd.read_csv(csv) for csv in csvs], ignore_index=True)
    df['Screener'] = screener['name']
    dfs.append(df)

  df = pd.concat(dfs, ignore_index=True)

  def resolve_etf(sector):
    return SECTOR_ETF[sector] if sector in SECTOR_ETF else ''

  df['Sector'] = df['Symbol'].apply(lambda x: read_value_from_json(x, 'sector', ''))
  df['Industry'] = df['Symbol'].apply(lambda x: read_value_from_json(x, 'industry', ''))
  df['ETF'] = df['Sector'].apply(lambda x: resolve_etf(x))

  df['FinancialsCurrentPrice'] = df['Symbol'].apply(lambda x: read_value_from_json(x, 'currentPrice', ''))
  df['FinancialsMarketCap'] = df['Symbol'].apply(lambda x: read_value_from_json(x, 'marketCap', ''))
  df['FinancialsVolume'] = df['Symbol'].apply(lambda x: read_value_from_json(x, 'volume', ''))
  df['FinancialsAverageVolume'] = df['Symbol'].apply(lambda x: read_value_from_json(x, 'averageVolume', ''))
  df['FinancialsTotalCash'] = df['Symbol'].apply(lambda x: read_value_from_json(x, 'totalCash', ''))
  df['FinancialsTotalDebt'] = df['Symbol'].apply(lambda x: read_value_from_json(x, 'totalDebt', ''))
  df['FinancialsQuickRatio'] = df['Symbol'].apply(lambda x: read_value_from_json(x, 'quickRatio', ''))
  df['FinancialsCurrentRatio'] = df['Symbol'].apply(lambda x: read_value_from_json(x, 'currentRatio', ''))
  df['FinancialsTotalRevenue'] = df['Symbol'].apply(lambda x: read_value_from_json(x, 'totalRevenue', ''))
  df['FinancialsDebtToEquity'] = df['Symbol'].apply(lambda x: read_value_from_json(x, 'debtToEquity', ''))
  df['FinancialsReturnOnAssets'] = df['Symbol'].apply(lambda x: read_value_from_json(x, 'returnOnAssets', ''))
  df['FinancialsReturnOnEquity'] = df['Symbol'].apply(lambda x: read_value_from_json(x, 'returnOnEquity', ''))
  df['FinancialsFreeCashflow'] = df['Symbol'].apply(lambda x: read_value_from_json(x, 'freeCashflow', ''))
  df['FinancialsOperatingCashflow'] = df['Symbol'].apply(lambda x: read_value_from_json(x, 'operatingCashflow', ''))

  df.to_csv(config['tickers']['target'], index=False)
