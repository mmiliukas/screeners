import json

import pandas as pd
import yfinance as yf

def save(symbols):
    for symbol in symbols:
        print(f'loading {symbol}')
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info or {}
            with open(f'./etfs/{symbol}.json', 'w') as file:
                file.write(json.dumps(info))
            ticker.history(period='max').to_csv(f'./etfs/{symbol}-history.csv')
        except Exception as e:
            print(f'failed to load "{symbol}"', e)

if __name__ == '__main__':
    df = pd.read_csv('./sector-etf.csv')

    for eu in df['EU']:
        save(eu.split(sep=','))

    for us in df['US']:
        save(us.split(sep=','))
