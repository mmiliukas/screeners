from datetime import timedelta
import matplotlib.pyplot as plt

import pandas as pd
import yfinance as yf

def adjust(date, days: int):
    adjusted = date + timedelta(days=days)
    adjusted = date if adjusted >= date else adjusted

    return adjusted.isoformat()

if __name__ == '__main__':
    sectors = pd.read_csv('./sector-etf.csv')
    daily_runs = pd.read_csv('./all.csv', parse_dates=['Date'])
    tickers = pd.read_json('./all-tickers.json')

    result = pd.merge(daily_runs, tickers, left_on="Symbol",right_on="symbol")
    result = result[['Symbol', 'Name', 'Date', 'sector', 'industry', 'country']].sort_values(by='sector')
    result = pd.merge(result, sectors, left_on="sector", right_on="Sector")
    result = result[['Symbol', 'Name', 'Date', 'sector', 'industry', 'country', 'EU', 'US']]

    print(result)

    index = 19
    ticker = yf.Ticker(result['Symbol'][index])
    us = yf.Ticker(result['US'][index].split(sep=',')[0])
    date = result['Date'][index].date()

    a = ticker.history(start=adjust(date, -84), end=adjust(date, 14))
    b = us.history(start=adjust(date, -84), end=adjust(date, 14))

    fig, ax = plt.subplots()
    a.plot(y='Close', ax=ax)
    b.plot(y='Close', ax=ax, secondary_y=True)

    plt.show()
