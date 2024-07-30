#!/usr/bin/env python

# Check why minas is lower by 2
"""
./million.py download max
./million.py date 100
./million.py signals 2022-12-01
./million.py backtest
"""

import datetime
import glob
import os
import sys
import warnings
from typing import List

import pandas as pd
import pandas_market_calendars as mcal

from screeners.million.download_history import download_history, read_history
from screeners.million.functions import (
    add_ranks,
    backtest,
    calculate_bollinger_bands,
    calculate_macd,
    calculate_minima,
    calculate_moving_average_crossover,
    calculate_parabolic_sar,
    calculate_rsi,
    calculate_stochastic_oscillator,
    check_parameters,
    mean_excluding_outliers,
)
from screeners.million.read_tickers import read_tickers
from screeners.utils import progress

warnings.filterwarnings("ignore")


def to_csv(df: pd.DataFrame, file_name: str):
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    df.to_csv(file_name)


def calculate_signals(until: datetime.date):
    tickers = read_tickers()

    for index, ticker in enumerate(tickers):
        progress("calculate signals", index + 1, len(tickers))

        history = read_history(f".cache/history/{ticker}.csv")
        history = history[history.index >= pd.to_datetime(until)]

        for distance in [5, 10, 30]:
            file_name = f".cache/signals/min/{ticker}_{distance}.csv"
            if os.path.exists(file_name):
                continue

            df = calculate_minima(history.copy(), distance)

            df["Symbol"] = ticker
            df["Strategy"] = "MIN"
            df["Param1"] = distance
            df["Param2"] = None
            df["Param3"] = None

            to_csv(df, file_name)

        for window in [9, 14, 21]:
            file_name = f".cache/signals/rsi/{ticker}_{window}.csv"
            if os.path.exists(file_name):
                continue

            df = calculate_rsi(history.copy(), window)

            df["Symbol"] = ticker
            df["Strategy"] = "RSI"
            df["Param1"] = window
            df["Param2"] = None
            df["Param3"] = None

            to_csv(df, file_name)

        for short in [5, 9, 14]:
            for long in [20, 21, 30]:
                file_name = f".cache/signals/ma/{ticker}_{short}_{long}.csv"
                if os.path.exists(file_name):
                    continue

                df = calculate_moving_average_crossover(history.copy(), short, long)

                df["Symbol"] = ticker
                df["Strategy"] = "MA"
                df["Param1"] = short
                df["Param2"] = long
                df["Param3"] = None

                to_csv(df, file_name)

        for fast in [8, 12, 16]:
            for slow in [18, 26, 34]:
                for signal in [5, 9, 13]:
                    file_name = (
                        f".cache/signals/macd/{ticker}_{fast}_{slow}_{signal}.csv"
                    )
                    if os.path.exists(file_name):
                        continue

                    df = calculate_macd(history.copy(), fast, slow, signal)

                    df["Symbol"] = ticker
                    df["Strategy"] = "MACD"
                    df["Param1"] = fast
                    df["Param2"] = slow
                    df["Param3"] = signal

                    to_csv(df, file_name)

        for acceleration in [0.05, 0.06, 0.07]:
            for maximum in [0.2, 0.25, 0.3]:
                file_name = f".cache/signals/sar/{ticker}_{acceleration}_{maximum}.csv"
                if os.path.exists(file_name):
                    continue

                df = calculate_parabolic_sar(history.copy(), acceleration, maximum)

                df["Symbol"] = ticker
                df["Strategy"] = "SAR"
                df["Param1"] = acceleration
                df["Param2"] = maximum
                df["Param3"] = None

                to_csv(df, file_name)

        for k_window in [10, 14, 20]:
            for d_window in [3, 5, 7]:
                file_name = f".cache/signals/stoch/{ticker}_{k_window}_{d_window}.csv"
                if os.path.exists(file_name):
                    continue

                df = calculate_stochastic_oscillator(history.copy(), k_window, d_window)

                df["Symbol"] = ticker
                df["Strategy"] = "STOCH"
                df["Param1"] = k_window
                df["Param2"] = d_window
                df["Param3"] = None

                to_csv(df, file_name)

        for window in [10, 20, 30]:
            for std_dev in [1.5, 2, 2.5]:
                file_name = f".cache/signals/bb/{ticker}_{window}_{std_dev}.csv"
                if os.path.exists(file_name):
                    continue

                df = calculate_bollinger_bands(history.copy(), window, std_dev)

                df["Symbol"] = ticker
                df["Strategy"] = "BB"
                df["Param1"] = window
                df["Param2"] = std_dev
                df["Param3"] = None

                to_csv(df, file_name)


def calculate_backtest():
    tickers = read_tickers()

    files = glob.glob(".cache/signals/*/*.csv")
    results = []

    for index, file in enumerate(files):
        progress("backtest", index + 1, len(files))

        symbol = os.path.basename(file).split("_")[0]
        if symbol not in tickers:
            continue

        df = read_history(file)
        if len(df) == 0:
            continue

        # XXXX
        # df = df[
        #     (df.index >= pd.to_datetime(datetime.date.fromisoformat('2022-06-15'))) &
        #     (df.index <= pd.to_datetime(datetime.date.fromisoformat('2023-07-01')))
        # ]
        # XXXX
        bt = backtest(df)
        if len(bt) == 0:
            continue

        bt["Symbol"] = df.iloc[0, df.columns.get_loc("Symbol")]  # type: ignore
        bt["Strategy"] = df.iloc[0, df.columns.get_loc("Strategy")]  # type: ignore
        bt["Param1"] = df.iloc[0, df.columns.get_loc("Param1")]  # type: ignore
        bt["Param2"] = df.iloc[0, df.columns.get_loc("Param2")]  # type: ignore
        bt["Param3"] = df.iloc[0, df.columns.get_loc("Param3")]  # type: ignore

        results.append(bt)

    df = pd.concat(results, ignore_index=True)
    to_csv(df, ".cache/backtest.csv")


def find():
    df = pd.read_csv(".cache/backtest.csv")
    # uz laikotarpi df = df[df[BuyDate] > start & df[BuyDate] <= end]
    # pagal rank'a
    df = (
        df.groupby(
            ["Symbol", "Strategy", "Expected Growth", "Param1", "Param2", "Param3"]
        )
        .agg(
            mean_days_held=("Days Held", mean_excluding_outliers),
            median_days_held=("Days Held", "median"),
            total_rows=("Buy Date", "size"),
            target_met_true=("Target Met", "sum"),
            min_days_held=("Days Held", "min"),
            max_days_held=("Days Held", "max"),
        )
        .reset_index()
    )
    df["percent_target_met"] = df["target_met_true"] / df["total_rows"] * 100
    print(df.info())


def calculate_positions(positions, date):
    total = 0
    for position in positions:
        symbol = position["Symbol"]
        amount = position["Amount"]
        df = read_history(f".cache/history/{symbol}.csv")
        open_price = df.loc[date.isoformat(), "Open"]
        total = total + open_price * amount
    return total


def calculate_buy_amount(total):
    prices = [
        # [2000, 250],
        [2540, 317],
        [3225, 403],
        [4096, 512],
        [5202, 650],
        [6607, 825],
    ]
    price = 250
    for limit, suggested_price in prices:
        if limit < total:
            price = suggested_price
    return price


df_backtest_raw = pd.read_csv(".cache/backtest.csv", parse_dates=["Buy Date"])
df_backtest_raw = df_backtest_raw[df_backtest_raw["Buy Date"] > pd.to_datetime('2023-07-01')]
df_backtest_raw = df_backtest_raw.fillna(-1)
df_backtest_raw = df_backtest_raw.sort_values("Buy Date", ascending=True)

df_backtest = pd.read_csv(".cache/backtest.csv", parse_dates=["Buy Date"])
df_backtest = df_backtest[
            (df_backtest["Buy Date"] >= pd.to_datetime('2022-06-15')) &
            (df_backtest["Buy Date"] <= pd.to_datetime('2023-07-01'))
        ]

df_backtest = df_backtest.sort_values("Buy Date", ascending=True)
df_backtest = df_backtest.fillna(-1)
df_backtest = (
    df_backtest.groupby(["Symbol", "Strategy", "Param1", "Param2", "Param3"])
    .agg(
        mean_days_held=("Days Held", mean_excluding_outliers),
        median_days_held=("Days Held", "median"),
        total_rows=("Buy Date", "size"),
        target_met_true=("Target Met", "sum"),
        min_days_held=("Days Held", "min"),
        max_days_held=("Days Held", "max"),
    )
    .reset_index()
)
df_backtest["percent_target_met"] = df_backtest["target_met_true"] / df_backtest["total_rows"] * 100
high_standard_count, lower_standard_count = check_parameters(df_backtest)
how_much = 8 if lower_standard_count > high_standard_count else 12
df_backtest = df_backtest[
            (df_backtest["percent_target_met"] == 100.0)
            & (df_backtest["total_rows"] > how_much)
            & (df_backtest["mean_days_held"] < 14)
            & (df_backtest["median_days_held"] < 8)
        ]

df_backtest = add_ranks(df_backtest, "median_days_held", ascending=True)
df_backtest = add_ranks(df_backtest, "mean_days_held", ascending=True)
df_backtest = add_ranks(df_backtest, "max_days_held", ascending=True)

df_backtest["rank"] = (
    df_backtest["rank_median_days_held"]
     + df_backtest["rank_mean_days_held"]
     + df_backtest["rank_max_days_held"]
 )

df_backtest = df_backtest.loc[df_backtest.groupby(['Symbol', 'Strategy'])['rank'].idxmin()]
df_backtest["Days To Drop"] = (df_backtest["median_days_held"] + 1) * 2 + 2
df_backtest = df_backtest[["Symbol", "Strategy", "Param1", "Param2", "Param3", "Days To Drop"]]


total_result = []

def get_candidates(date):
    a = df_backtest_raw["Buy Date"]#.shift(1)
    b = pd.to_datetime(date)
    today_candidates = df_backtest_raw[a == b]
    # print(df)

    result = []
    for idx, row in today_candidates.iterrows():
        df2 = df_backtest[
            (df_backtest["Symbol"] == row["Symbol"])
            & (df_backtest["Strategy"] == row["Strategy"])
            & (df_backtest["Param1"] == row["Param1"])
            & (df_backtest["Param2"] == row["Param2"])
            & (df_backtest["Param3"] == row["Param3"])
        ]
        if len(df2) > 0:
            total_result.append(row)
            result.append(df2)

    df3 = pd.concat(result) if len(result) > 0 else pd.DataFrame([])
    if len(df3) > 0:
        df3 = df3.sort_values("Days To Drop")

    return df3


def run(start_date, end_date):
    nyse = mcal.get_calendar("NYSE")
    schedule = nyse.schedule(start_date=start_date, end_date=end_date)

    budget = 2_000
    positions = []
    history = []
    counter = 1_000_000
    fee = 1.5

    daily = []
    total = len(schedule.index.to_list())
    for dateidx, date in enumerate(schedule.index.to_list()):
        date = date.date()
        progress(f"{date.isoformat()}", dateidx + 1, total)

        in_positions = calculate_positions(positions, date)
        in_budget = budget
        in_total = in_positions + in_budget

        buy_amount = calculate_buy_amount(in_total)
        candidates = get_candidates(date)

        daily.append({
            "Date": date,
            "Buy Amount": buy_amount,
            "In Bank": in_budget,
            "In Positions": in_positions,
            "In Total": in_total,
        })
        # print(date, candidate["Symbol"], candidate["Strategy"], buy_amount)



        for idx, candidate in candidates.iterrows():
            # print(buy_amount)
            if buy_amount + fee < budget:  # type: ignore
                # print("BUY", buy_amount)
                df = read_history(f'.cache/history/{candidate["Symbol"]}.csv')
                price = df.loc[date.isoformat(), "Open"]
                how_much = int((buy_amount - fee * 2)/ price)  # type: ignore
                total_cost = how_much * price  # type: ignore
                counter = counter + 20
                buy_ref = counter
                history.append(
                    {
                        "Date": date,
                        "Side": "BOUGHT",
                        "Symbol": candidate["Symbol"],
                        "Amount": how_much,
                        "Price": price,
                        "Fee": fee,
                        "Strategy": candidate["Strategy"],
                        "Param1": candidate["Param1"],
                        "Param2": candidate["Param2"],
                        "Param3": candidate["Param3"],
                        "Ref": buy_ref
                    }
                )
                positions.append(
                    {
                        "Symbol": candidate["Symbol"],
                        "Amount": how_much,
                        "Price": price,
                        "Buy Date": date,
                        "Days To Drop": candidate["Days To Drop"],
                        "Strategy": candidate["Strategy"],
                        "Param1": candidate["Param1"],
                        "Param2": candidate["Param2"],
                        "Param3": candidate["Param3"],
                        "Ref": buy_ref
                    }
                )
                budget = budget - (total_cost + fee)  # type: ignore

        new_positions = []
        for position in positions:
            df = read_history(f'.cache/history/{position["Symbol"]}.csv')
            high = df.loc[date.isoformat(), "High"]
            low = df.loc[date.isoformat(), "Low"]
            close = df.loc[date.isoformat(), "Close"]


            if position["Price"] * 1.036 <= high:
                history.append(
                    {
                        "Date": date,
                        "Side": "SELL_WIN",
                        "Symbol": position["Symbol"],
                        "Amount": position["Amount"],
                        "Price": position["Price"] * 1.036,
                        "Fee": fee,
                        "Strategy": position["Strategy"],
                        "Param1": position["Param1"],
                        "Param2": position["Param2"],
                        "Param3": position["Param3"],
                        "Ref": position["Ref"]
                    }
                )
                budget = budget + position["Amount"] * position["Price"] * 1.036 - fee
            elif position["Price"] * 0.8 > low:
                history.append(
                    {
                        "Date": date,
                        "Side": "SELL_STOP_LOSS",
                        "Symbol": position["Symbol"],
                        "Amount": position["Amount"],
                        "Price": position["Price"] * 0.8,
                        "Fee": fee,
                        "Strategy": position["Strategy"],
                        "Param1": position["Param1"],
                        "Param2": position["Param2"],
                        "Param3": position["Param3"],
                        "Ref": position["Ref"]
                    }
                )
                budget = budget + position["Amount"] * position["Price"] * 0.9 - 1
            elif position["Days To Drop"] == 0:
                history.append(
                    {
                        "Date": date,
                        "Side": "SELL_OVERDUE",
                        "Symbol": position["Symbol"],
                        "Amount": position["Amount"],
                        "Price": close,
                        "Fee": fee,
                        "Strategy": position["Strategy"],
                        "Param1": position["Param1"],
                        "Param2": position["Param2"],
                        "Param3": position["Param3"],
                        "Ref": position["Ref"]
                    }
                )
                budget = budget + position["Amount"] * close - fee
            else:
                new_positions.append(position)
                position["Days To Drop"] = position["Days To Drop"] - 1

        positions = new_positions

    return (history, positions, daily)

def main(args: List[str]):

    if args[0] == "date":
        days = int(args[1])
        date = datetime.date.today() - datetime.timedelta(days=days)
        print(date.isoformat())

    if args[0] == "download":
        tickers = read_tickers()
        period = args[1]
        download_history(tickers, period=period, to=".cache/history")

    if args[0] == "signals":
        until = datetime.date.fromisoformat(args[1])
        calculate_signals(until)

    if args[0] == "backtest":
        calculate_backtest()

    if args[0] == "run":
        start_date = datetime.date.fromisoformat(args[1])
        end_date = datetime.date.fromisoformat(args[2])
        (history, positions, daily) = run(start_date, end_date)
        print("ETALON")

        print(df_backtest)
        df_backtest.to_csv(".cache/etalon.csv")

        print("-" * 20)

        daily_df = pd.DataFrame(daily)
        daily_df.to_csv(".cache/daily.csv")
        print(daily_df)

        print("-" * 20)

        history_df = pd.DataFrame(history)
        history_df.to_csv(".cache/history.csv")
        print(history_df)

        print("-" * 20)

        df_positions = pd.DataFrame(positions)
        df_positions.to_csv(".cache/positions.csv")
        print(df_positions)


if __name__ == "__main__":
    args = sys.argv[1:] if len(sys.argv) > 1 else ["none"]
    main(args)
