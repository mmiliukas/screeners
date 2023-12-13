import math
import matplotlib.pyplot as plt

from datetime import timedelta

import pandas as pd
import yfinance as yf

def calculate_stock_correlation(stock1_prices, stock2_prices):
    # Calculate the average price for each stock
    stock1_avg_price = sum(stock1_prices) / len(stock1_prices)
    stock2_avg_price = sum(stock2_prices) / len(stock2_prices)

    # Calculate the daily deviation for each stock
    stock1_deviations = [price - stock1_avg_price for price in stock1_prices]
    stock2_deviations = [price - stock2_avg_price for price in stock2_prices]

    # Calculate the squared daily deviations for each stock
    stock1_squared_deviations = [deviation ** 2 for deviation in stock1_deviations]
    stock2_squared_deviations = [deviation ** 2 for deviation in stock2_deviations]

    # Calculate the product of squared deviations for each day
    product_of_deviations = [dev1 * dev2 for dev1, dev2 in zip(stock1_squared_deviations, stock2_squared_deviations)]

    # Calculate the standard deviation for each stock
    stock1_std_dev = math.sqrt(sum(stock1_squared_deviations))
    stock2_std_dev = math.sqrt(sum(stock2_squared_deviations))

    # Calculate the correlation
    correlation = sum(product_of_deviations) / (stock1_std_dev * stock2_std_dev)

    return correlation

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

    symbol = result['Symbol'][index]
    ticker = yf.Ticker(symbol)
    us = yf.Ticker(result['US'][index].split(sep=',')[0]) # taking only first available ETF
    date = result['Date'][index].date()

    a = ticker.history(start=adjust(date, -84), end=adjust(date, 14))
    b = us.history(start=adjust(date, -84), end=adjust(date, 14))

    correlation = calculate_stock_correlation(a['Close'], b['Close'])
    print(f'correlation for {symbol} = {correlation}')

    fig, ax = plt.subplots()
    a.plot(y='Close', ax=ax)
    b.plot(y='Close', ax=ax, secondary_y=True)

    plt.show()
