import yaml
import glob
import json
import pandas as pd
import yfinance as yf

from datetime import timedelta
from requests_cache import CachedSession

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

with open('yahoo.yml', 'r') as file:
  config = yaml.safe_load(file)

# https://requests-cache.readthedocs.io/en/stable/user_guide.html
cache_session = CachedSession(config['yfinance']['cache'],
                              backend='filesystem',
                              expire_after=timedelta(days=config['yfinance']['days']))

def get_ratios(symbol: str, index: int):
  ticker = yf.Ticker(symbol, session=cache_session)

  balance_sheet: pd.DataFrame = ticker.get_balance_sheet(freq='quarterly', as_dict=False) # type: ignore
  if balance_sheet.empty:
    return pd.Series([0, 0, 0])

  quarter = balance_sheet.columns.to_list()[index]

  total_assets = balance_sheet.loc['TotalAssets'][quarter] if 'TotalAssets' in balance_sheet.index else 0
  non_current_assets = balance_sheet.loc['TotalNonCurrentAssets'][quarter] if 'TotalNonCurrentAssets' in balance_sheet.index else 0

  current_assets = total_assets - non_current_assets

  a = balance_sheet.loc['TotalLiabilitiesNetMinorityInterest'][quarter] if 'TotalLiabilitiesNetMinorityInterest' in balance_sheet.index else 0
  b = balance_sheet.loc['TotalNonCurrentLiabilitiesNetMinorityInterest'][quarter] if 'TotalNonCurrentLiabilitiesNetMinorityInterest' in balance_sheet.index else 0

  current_liabilities = a - b

  inventory = balance_sheet.loc['Inventory'][quarter] if 'Inventory' in balance_sheet.index else 0
  cash_and_cash_equivalents = balance_sheet.loc['CashAndCashEquivalents'][quarter] if 'CashAndCashEquivalents' in balance_sheet.index else 0

  try:
    current_ratio = current_assets / current_liabilities
  except:
    current_ratio = 0

  try:
    quick_ratio = (current_assets - inventory) / current_liabilities
  except:
    quick_ratio = 0

  try:
    cash_ratio = cash_and_cash_equivalents / current_liabilities
  except:
    cash_ratio = 0

  return pd.Series([current_ratio, quick_ratio, cash_ratio])

if __name__ == '__main__':
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

  df[['CurrentRatio', 'QuickRatio', 'CashRatio']] = df['Symbol'].apply(lambda x: get_ratios(x, 0))

  # TODO: store inside a black list
  df = df[df['FinancialsCurrentRatio'] >= 0.5]

  df.to_csv(config['tickers']['target'], index=False)
