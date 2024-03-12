import glob
import json
import pandas as pd

from screeners.config import config
from screeners.etfs import resolve_etf
from screeners.tickers import get_tickers, mark_as_ignored, get_etfs

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

json_cache = {}

def read_value_from_json(symbol: str, key: str, default = None):
  if symbol not in json_cache:
    with open(config['tickers']['cache_name'] + symbol + '.json') as file:
      json_cache[symbol] = json.load(file)
  ticker = json_cache[symbol]
  if len(ticker) == 0:
    return default
  return ticker[0][key] if key in ticker[0] else default

def enrich_tickers(symbols) -> pd.DataFrame:
  df = pd.DataFrame({ 'Symbol': symbols })

  df['Name'] = df['Symbol'].apply(lambda _: read_value_from_json(_, 'longName', pd.NA))
  df['Sector'] = df['Symbol'].apply(lambda _: read_value_from_json(_, 'sector', pd.NA))
  df['Industry'] = df['Symbol'].apply(lambda _: read_value_from_json(_, 'industry', pd.NA))
  df['ETF'] = df['Sector'].apply(lambda _: resolve_etf(_))

  enrich_screeners(df)

  df['FinancialsMarketCap'] = df['Symbol'].apply(lambda _: read_value_from_json(_, 'marketCap', pd.NA))
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

  return df

if __name__ == '__main__':

  df = enrich_tickers(get_tickers())

  filter = df['FinancialsCurrentRatio'] >= config['tickers']['filter']['FinancialsCurrentRatio']
  (df[filter]).to_csv(config['tickers']['target'], index=False)

  mark_as_ignored(df[~filter])

  df = enrich_tickers(get_etfs())
  df.to_csv('./tickers-etfs.csv', index=False)
