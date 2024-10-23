from datetime import date

import pandas as pd
import yfinance as yf


def download(
    ticker: str,
    start: str | date | None = None,
    end: str | date | None = None,
    interval="1d",
    period: str = "max",
    progress=False,
    skip_transform=False,
) -> pd.DataFrame:
    group_by = "column" if skip_transform else "ticker"
    history = yf.download(
        ticker,
        start=start,
        end=end,
        interval=interval,
        period=period,
        progress=progress,
        group_by=group_by,
    )

    if not skip_transform:
        history = history[ticker]

    history.index = history.index.date
    history.index.name = "Date"

    return history
