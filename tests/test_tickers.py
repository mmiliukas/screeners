import pandas as pd


def test_tickers_are_unique():
    df = pd.read_csv("./tickers.csv")
    assert not df["Symbol"].duplicated().any()


def test_tickers_to_have_required_columns():
    columns = [
        "Symbol",
        "Name",
        "Sector",
        "Industry",
        "ETF",
        "Winners 1",
        "Winners 5",
        "Winners 10",
        "Winners 100",
        "Loosers 1",
        "Loosers 5",
        "Loosers 10",
        "Loosers 100",
        "Random 1",
        "Random 5",
        "Random 10",
        "Random 100",
        "Screener",
    ]
    df = pd.read_csv("./tickers.csv")

    for column in columns:
        assert len(df[df[column].isna()]) == 0
