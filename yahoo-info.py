import os
import json
import pandas as pd
import yfinance as yf

if __name__ == '__main__':
    df = pd.read_csv('./runs/all.csv')
    tickers = [symbol for symbol in df['Symbol']]
    for ticker in tickers:
        path = './tickers/' + ticker + '.json'
        path_exists = os.path.exists(path)

        if not path_exists:
            print('getting ticker details', ticker)

            result = yf.Ticker(ticker)
            with open(path, 'w') as f:
                f.write(json.dumps(result.info))
