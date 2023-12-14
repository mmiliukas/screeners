from datetime import timedelta

import numpy as np
import pandas as pd
import yfinance as yf

def adjust(date, days: int):
    adjusted = date + timedelta(days=days)
    adjusted = date if adjusted >= date else adjusted

    return adjusted.isoformat()

def correlation(row):
    print(row['symbol'])

    ticker = yf.Ticker(row['symbol'])
    us = yf.Ticker(row['us'].split(sep=',')[0])
    date = row['date'].date()

    ticker_history = ticker.history(start=adjust(date, -90), end=adjust(date, 14))
    us_history = us.history(start=adjust(date, -90), end=adjust(date, 14))

    try:
        coef = np.corrcoef(ticker_history['Close'], us_history['Close'])
        return coef[0][1]
    except Exception:
        print('failed', row['symbol'])
        return None

if __name__ == '__main__':
    sectors = pd.read_csv('./sector-etf.csv').rename(str.lower, axis='columns')
    runs = pd.read_csv('./all.csv', parse_dates=['Date']).rename(str.lower, axis='columns')
    tickers = pd.read_json('./all-tickers.json').rename(str.lower, axis='columns')

    result = pd.merge(runs, tickers, left_on="symbol",right_on="symbol")
    result = result[['symbol', 'sector', 'industry', 'date']]

    result = pd.merge(result, sectors, left_on="sector", right_on="sector")
    result = result[['symbol', 'sector', 'industry', 'date', 'us']]

    corr = []

    for index, row in result.iterrows():
        corr.append(correlation(row))

    result['corr'] = corr

    result.to_csv('./corr.csv')
