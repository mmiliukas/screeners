import json
import pandas as pd
import yfinance as yf

if __name__ == '__main__':
    df = pd.read_csv('./runs/all.csv')

    tickers = [symbol for symbol in df['Symbol']]
    tickers_info = []

    for ticker in tickers:
        path = './tickers/' + ticker + '.json'
        result = yf.Ticker(ticker)
        tickers_info.append(result.info or {})

        with open(path, 'w') as f:
            f.write(json.dumps(result.info or {}))

    with open('./tickers.json', 'w') as f:
        f.write(json.dumps(tickers_info))

