import sys
import pandas as pd

from screeners.telegram import log_to_telegram

if __name__ == '__main__':
  bot_token, channel_id = sys.argv[1:]

  tickers = len(pd.read_csv('./tickers.csv'))
  ignore = len(pd.read_csv('./tickers-ignored.csv'))

  log_to_telegram(f'DAILY RUN: {tickers} tickers matched and {ignore} ignored', bot_token, channel_id)
