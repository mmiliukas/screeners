from typing import List

import pandas as pd


def read_tickers() -> List[str]:
    url = "https://raw.githubusercontent.com/mmiliukas/screeners/main/tickers.csv"

    tickers = pd.read_csv(url)

    tickers = tickers[tickers["Exchange"] != "PNK"]
    # screeners = ["Random 5", "Random 10", "Winners 5", "Winners 10"]
    # screeners = ["Winners 5", "Winners 10"]
    # screeners = ["Winners 5"]
    screeners = ["Random 10"]

    tickers = tickers[tickers[screeners].gt(0).any(axis=1)]

    return tickers["Symbol"].to_list()
    # return ["ACIU"]
