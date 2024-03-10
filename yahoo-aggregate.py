import glob
import json
import pandas as pd

from screeners.config import config
from screeners.etfs import resolve_etf

def get_ratios(symbol: str, index: int):
  balance_sheet = pd.read_csv(f'./tickers-balance/{symbol}.csv', index_col=0)

  if balance_sheet.empty:
    return pd.Series([pd.NA, pd.NA, pd.NA])

  quarter = balance_sheet.columns.to_list()[index]

  total_assets = balance_sheet.loc['TotalAssets'][quarter] if 'TotalAssets' in balance_sheet.index else pd.NA
  non_current_assets = balance_sheet.loc['TotalNonCurrentAssets'][quarter] if 'TotalNonCurrentAssets' in balance_sheet.index else pd.NA

  current_assets = total_assets - non_current_assets

  a = balance_sheet.loc['TotalLiabilitiesNetMinorityInterest'][quarter] if 'TotalLiabilitiesNetMinorityInterest' in balance_sheet.index else pd.NA
  b = balance_sheet.loc['TotalNonCurrentLiabilitiesNetMinorityInterest'][quarter] if 'TotalNonCurrentLiabilitiesNetMinorityInterest' in balance_sheet.index else pd.NA

  current_liabilities = a - b

  inventory = balance_sheet.loc['Inventory'][quarter] if 'Inventory' in balance_sheet.index else pd.NA
  cash_and_cash_equivalents = balance_sheet.loc['CashAndCashEquivalents'][quarter] if 'CashAndCashEquivalents' in balance_sheet.index else pd.NA

  try:
    current_ratio = current_assets / current_liabilities
  except:
    current_ratio = pd.NA

  try:
    quick_ratio = (current_assets - inventory) / current_liabilities
  except:
    quick_ratio = pd.NA

  try:
    cash_ratio = cash_and_cash_equivalents / current_liabilities
  except:
    cash_ratio = pd.NA

  return pd.Series([current_ratio, quick_ratio, cash_ratio])

def enrich_screeners_names(row):
  names = []
  for screener in config['screeners']:
    if row[screener['name']] > 0:
      names.append(screener['name'])
  return ','.join(names)

def enrich_screeners(df: pd.DataFrame):
  for screener in config['screeners']:
    csvs = glob.glob(f'{screener["cache_name"]}/*.csv')
    all = pd.concat([pd.read_csv(csv) for csv in csvs])
    df[screener['name']] = df['Symbol'].apply(lambda _: len(all[all['Symbol'] == _]))

  df['Screener'] = df.apply(enrich_screeners_names, axis=1)

def get_unique_symbols():
  runs = [screener['cache_name'] for screener in config['screeners']]

  csvs = []
  for run in runs: csvs.extend(glob.glob(f'{run}/*.csv'))

  df = pd.concat([pd.read_csv(csv) for csv in csvs])
  return df['Symbol'].unique()

json_cache = {}

def read_value_from_json(symbol: str, key: str, default = None):
  if symbol not in json_cache:
    with open(config['tickers']['cache_name'] + symbol + '.json') as file:
      json_cache[symbol] = json.load(file)
  ticker = json_cache[symbol]
  if len(ticker) == 0:
    return default
  return ticker[0][key] if key in ticker[0] else default

if __name__ == '__main__':

  df = pd.DataFrame({ 'Symbol': get_unique_symbols() })

  df['Name'] = df['Symbol'].apply(lambda _: read_value_from_json(_, 'longName', pd.NA))
  df['Sector'] = df['Symbol'].apply(lambda _: read_value_from_json(_, 'sector', pd.NA))
  df['Industry'] = df['Symbol'].apply(lambda _: read_value_from_json(_, 'industry', pd.NA))
  df['ETF'] = df['Sector'].apply(lambda _: resolve_etf(_))

  enrich_screeners(df)

  df['FinancialsCurrentPrice'] = df['Symbol'].apply(lambda _: read_value_from_json(_, 'currentPrice', pd.NA))
  df['FinancialsMarketCap'] = df['Symbol'].apply(lambda _: read_value_from_json(_, 'marketCap', pd.NA))
  df['FinancialsVolume'] = df['Symbol'].apply(lambda _: read_value_from_json(_, 'volume', pd.NA))
  df['FinancialsAverageVolume'] = df['Symbol'].apply(lambda _: read_value_from_json(_, 'averageVolume', pd.NA))
  df['FinancialsTotalCash'] = df['Symbol'].apply(lambda _: read_value_from_json(_, 'totalCash', pd.NA))
  df['FinancialsTotalDebt'] = df['Symbol'].apply(lambda _: read_value_from_json(_, 'totalDebt', pd.NA))
  df['FinancialsQuickRatio'] = df['Symbol'].apply(lambda _: read_value_from_json(_, 'quickRatio', pd.NA))
  df['FinancialsCurrentRatio'] = df['Symbol'].apply(lambda _: read_value_from_json(_, 'currentRatio', pd.NA))
  df['FinancialsTotalRevenue'] = df['Symbol'].apply(lambda _: read_value_from_json(_, 'totalRevenue', pd.NA))
  df['FinancialsDebtToEquity'] = df['Symbol'].apply(lambda _: read_value_from_json(_, 'debtToEquity', pd.NA))
  df['FinancialsReturnOnAssets'] = df['Symbol'].apply(lambda _: read_value_from_json(_, 'returnOnAssets', pd.NA))
  df['FinancialsReturnOnEquity'] = df['Symbol'].apply(lambda _: read_value_from_json(_, 'returnOnEquity', pd.NA))
  df['FinancialsFreeCashflow'] = df['Symbol'].apply(lambda _: read_value_from_json(_, 'freeCashflow', pd.NA))
  df['FinancialsOperatingCashflow'] = df['Symbol'].apply(lambda _: read_value_from_json(_, 'operatingCashflow', pd.NA))

  df[['CurrentRatio', 'QuickRatio', 'CashRatio']] = df['Symbol'].apply(lambda _: get_ratios(_, 0))

  df = df[df['FinancialsCurrentRatio'] >= config['tickers']['filter']['FinancialsCurrentRatio']]

  # TODO: store inside a black list
  # TODO: get list of stocks from ETF
  df.to_csv(config['tickers']['target'], index=False)
