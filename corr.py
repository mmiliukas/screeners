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

    a = None
    b = None

    try:
        a = ticker_history['Close'].corr(us_history['Close'])
    except Exception:
        pass

    try:
        b = np.corrcoef(ticker_history['Close'], us_history['Close'])[0][1]
    except Exception:
        pass

    return a, b

if __name__ == '__main__':
    sectors = pd.read_csv('./sector-etf.csv').rename(str.lower, axis='columns')
    runs = pd.read_csv('./all.csv', parse_dates=['Date']).rename(str.lower, axis='columns')
    tickers = pd.read_json('./all-tickers.json').rename(str.lower, axis='columns')

    result = pd.merge(runs, tickers, left_on="symbol",right_on="symbol")
    result = result[['symbol', 'sector', 'industry', 'date']]

    result = pd.merge(result, sectors, left_on="sector", right_on="sector")
    result = result[['symbol', 'sector', 'industry', 'date', 'us']]

    corr_numpy = []
    corr_pandas = []

    for index, row in result.iterrows():
        a, b = correlation(row)
        corr_pandas.append(a)
        corr_numpy.append(b)

    result['corr_pandas'] = corr_pandas
    result['corr_numpy'] = corr_numpy

    result.to_csv('./corr.csv')
