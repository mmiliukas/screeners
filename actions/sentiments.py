import json
import logging
import os

import pandas as pd
import requests

logger = logging.getLogger(__name__)


def download(api_key: str, ticker: str, time_from: str, limit: int):
    url = "https://www.alphavantage.co/query"

    response = requests.get(
        url,
        {
            "function": "NEWS_SENTIMENT",
            "tickers": ticker,
            "apikey": api_key,
            "time_from": time_from,
            "limit": limit,
        },
    )

    return response.json()


def sentiments(
    api_key: str,
    ticker: str,
    time_from="20200101T0000",
    limit=1_000,
    force=False,
) -> None:
    file_name = f"./sentiments/cache/{ticker}_{time_from}_{limit}.json"

    if os.path.exists(file_name):
        if not force:
            logger.info(f"sentiments for '{ticker}' already downloaded, aborting")
            return

        logger.info(f"sentiments for '{ticker}' already downloaded, loading from cache")
        with open(file_name, "r") as file:
            data = json.load(file)

    else:
        logger.info(f"downloading sentiments for '{ticker}' from '{time_from}'")
        data = download(api_key, ticker, time_from, limit)

        with open(file_name, "w") as file:
            file.write(json.dumps(data))

    flattened_data = []
    for row in data["feed"]:
        for sentiment in row["ticker_sentiment"]:
            copy = dict()
            copy["title"] = row["title"]
            copy["time_published"] = row["time_published"]
            copy["url"] = row["url"]
            for prop in [
                "ticker",
                "relevance_score",
                "ticker_sentiment_label",
                "ticker_sentiment_score",
            ]:
                copy[prop] = sentiment[prop]
            flattened_data.append(copy)

    if len(flattened_data) == 0:
        logger.info(f"no sentiments data found, aborting")
        return

    df = pd.DataFrame(flattened_data)
    for ticker in list(df["ticker"].unique()):
        file_name = f"./sentiments/{ticker}.csv"
        filtered = df[df["ticker"] == ticker]

        if not filtered.empty:
            if os.path.exists(file_name):
                existing = pd.read_csv(file_name)
                pd.concat([existing, filtered]).to_csv(file_name, index=False)
            else:
                filtered.to_csv(file_name, index=False)
