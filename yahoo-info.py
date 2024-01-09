import json
import pandas as pd
import yfinance as yf

def ticker_summary(ticker):
    return {
        'volume': ticker.get('volume') or 0,
        'regularMarketVolume': ticker.get('regularMarketVolume') or 0,
        'averageVolume': ticker.get('averageVolume') or 0,
        'averageVolume10days': ticker.get('averageVolume10days') or 0,
        'averageDailyVolume10Day': ticker.get('averageDailyVolume10Day') or 0,
        'marketCap': ticker.get('marketCap') or 0,
        'fiftyTwoWeekLow': ticker.get('fiftyTwoWeekLow') or 0,
        'fiftyTwoWeekHigh': ticker.get('fiftyTwoWeekHigh') or 0,
        'fiftyDayAverage': ticker.get('fiftyDayAverage') or 0,
        'industry': ticker.get('industry') or '',
        'industryKey': ticker.get('industryKey') or '',
        'industryDisp': ticker.get('industryDisp') or '',
        'sector': ticker.get('sector') or '',
        'sectorKey': ticker.get('sectorKey') or '',
        'sectorDisp': ticker.get('sectorDisp') or '',
        'city': ticker.get('city') or '',
        'country': ticker.get('country') or '',
        'symbol': ticker.get('symbol') or '',
    }

if __name__ == '__main__':
    all_gainers = pd.read_csv('./all.csv')
    all_loosers = pd.read_csv('./all-loosers.csv')

    df = pd.concat([all_gainers, all_loosers])

    tickers = list(df['Symbol'].unique())
    tickers_info = []

    for ticker in tickers:
        path = './tickers/' + ticker + '.json'
        result = yf.Ticker(ticker)
        tickers_info.append(result.info or {})

        with open(path, 'w') as f:
            f.write(json.dumps([result.info or {}]))

    with open('./all-tickers.json', 'w') as f:
        f.write(json.dumps(list(map(ticker_summary, tickers_info))))
