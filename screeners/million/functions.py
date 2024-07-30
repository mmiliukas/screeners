import pandas as pd
import yfinance as yf
from scipy.signal import find_peaks
from ta.trend import ADXIndicator, PSARIndicator


def calculate_minima(data, distance):
    data["Buy"] = False

    neg_data = -data["Close"]
    peaks, _ = find_peaks(neg_data, distance=distance)
    data.iloc[peaks, data.columns.get_loc("Buy")] = True

    return data


def calculate_rsi(data, window):
    delta = data["Close"].diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    data["RSI"] = rsi
    data["Buy"] = False

    buy_dates = data[data["RSI"] < 30].index

    i = 0
    while i < len(buy_dates) - 1:
        if (buy_dates[i + 1] - buy_dates[i]).days == 1:
            data.at[buy_dates[i + 1], "Buy"] = True
            i += 2  # Skip the next date
        else:
            i += 1

    return data


def calculate_moving_average_crossover(data, short_window, long_window):
    data["Short MA"] = data["Close"].rolling(window=short_window).mean()
    data["Long MA"] = data["Close"].rolling(window=long_window).mean()
    data["Buy"] = (data["Short MA"] > data["Long MA"]) & (
        data["Short MA"].shift(1) <= data["Long MA"].shift(1)
    )
    return data


def calculate_macd(data, fast_window, slow_window, signal_window):
    data["EMA Fast"] = data["Close"].ewm(span=fast_window, adjust=False).mean()
    data["EMA Slow"] = data["Close"].ewm(span=slow_window, adjust=False).mean()
    data["MACD"] = data["EMA Fast"] - data["EMA Slow"]
    data["Signal Line"] = data["MACD"].ewm(span=signal_window, adjust=False).mean()
    data["Buy"] = (data["MACD"] > data["Signal Line"]) & (
        data["MACD"].shift(1) <= data["Signal Line"].shift(1)
    )
    return data


def calculate_parabolic_sar(data, acceleration, maximum):
    data["SAR"] = PSARIndicator(
        data["High"], data["Low"], data["Close"], step=acceleration, max_step=maximum
    ).psar()
    data["Buy"] = data["Close"] > data["SAR"]
    return data


def calculate_stochastic_oscillator(data, k_window, d_window):
    data["L14"] = data["Low"].rolling(window=k_window).min()
    data["H14"] = data["High"].rolling(window=k_window).max()
    data["%K"] = 100 * ((data["Close"] - data["L14"]) / (data["H14"] - data["L14"]))
    data["%D"] = data["%K"].rolling(window=d_window).mean()
    data["Buy"] = (
        (data["%K"] < 20)
        & (data["%K"] > data["%D"])
        & (data["%K"].shift(1) <= data["%D"].shift(1))
    )
    return data


def calculate_bollinger_bands(data, window, std_dev):
    data["Middle Band"] = data["Close"].rolling(window=window).mean()
    data["Std Dev"] = data["Close"].rolling(window=window).std()
    data["Upper Band"] = data["Middle Band"] + (std_dev * data["Std Dev"])
    data["Lower Band"] = data["Middle Band"] - (std_dev * data["Std Dev"])
    data["BB"] = data["Close"] < data["Lower Band"]

    data["Buy"] = False
    buy_dates = data[data["BB"]].index

    i = 0
    while i < len(buy_dates) - 1:
        if (buy_dates[i + 1] - buy_dates[i]).days == 1:
            data.at[buy_dates[i + 1], "Buy"] = True
            i += 2  # Skip the next date
        else:
            i += 1

    return data

def mean_excluding_outliers(series):
    mean = series.mean()
    std_dev = series.std()
    filtered_series = series[
        (series >= mean - 3 * std_dev) & (series <= mean + 3 * std_dev)
    ]
    result = filtered_series.mean()
    return mean if pd.isna(result) else result

def backtest(data, signal_col="Buy", sell_targets=[0.036]):
    # Find the next valid index after the current buy signal
    buys = data[data[signal_col]].index.to_series().shift(-1).dropna()
    valid_buys = [buy for buy in buys if buy in data.index]

    results = []
    for buy_date in valid_buys:
        buy_price = data.loc[buy_date, "Open"]
        for target in sell_targets:
            sell_info = {
                "Buy Date": buy_date,
                "Buy Price": buy_price,
                "Expected Growth": target * 100,
            }
            sell_price_target = buy_price * (1 + target)
            sell_data = data.loc[buy_date:]

            # Check for sell conditions
            sell = sell_data[sell_data["High"] >= sell_price_target]
            if not sell.empty:
                sell_date = sell.index[0]
                sell_price = sell_price_target
                # Calculate actual trading days held (excluding weekends and holidays)
                days_held = sell_data.loc[:sell_date].index.size - 1
                sell_info.update(
                    {
                        "Sell Date": sell_date,
                        "Sell Price": sell_price,
                        "Days Held": days_held,
                        "Return Raw": (sell_price - buy_price),
                        "Target Met": True,
                    }
                )
            else:
                # Calculate actual trading days held (excluding weekends and holidays)
                days_held = sell_data.index.size - 1
                sell_info.update(
                    {
                        "Sell Date": None,
                        "Sell Price": None,
                        "Days Held": None,
                        "Return Raw": None,
                        "Target Met": False,
                    }
                )
            results.append(sell_info.copy())

    return pd.DataFrame(results)


def check_parameters(grouped_df):
    high_standard_df = grouped_df[
        (grouped_df["percent_target_met"] == 100.0)
        & (grouped_df["total_rows"] > 12)
        & (grouped_df["mean_days_held"] < 14)
        & (grouped_df["median_days_held"] < 8)
    ]
    high_standard_unique_strategies = high_standard_df["Strategy"].nunique()

    lower_standard_df = grouped_df[
        (grouped_df["percent_target_met"] == 100.0)
        & (grouped_df["total_rows"] > 8)
        & (grouped_df["mean_days_held"] < 14)
        & (grouped_df["median_days_held"] < 8)
    ]
    lower_standard_unique_strategies = lower_standard_df["Strategy"].nunique()

    return high_standard_unique_strategies, lower_standard_unique_strategies


def add_ranks(df, rank_column, ascending=True):
    df[f"rank_{rank_column}"] = df.groupby(["Symbol", "Strategy"])[rank_column].rank(
        ascending=ascending
    )
    return df


# Modify process_grouped_df to accept and return old_raw_results_for_visual_df
def process_grouped_df(
    grouped_df, raw_results_df, ticker, old_raw_results_for_visual_df
):
    high_standard_count, lower_standard_count = check_parameters(grouped_df)

    if lower_standard_count > high_standard_count:
        new_grouped_df = grouped_df[
            (grouped_df["percent_target_met"] == 100.0)
            # svarbu per metus + kiek menesiu norim backtestinti
            # 2 metu
            # production'e 1 metu
            # don't forget to include fee 2 per trade
            & (grouped_df["total_rows"] > 8)
            & (grouped_df["mean_days_held"] < 14)
            & (grouped_df["median_days_held"] < 8)
        ].copy()
    else:
        new_grouped_df = grouped_df[
            (grouped_df["percent_target_met"] == 100.0)
            & (grouped_df["total_rows"] > 12)
            & (grouped_df["mean_days_held"] < 14)
            & (grouped_df["median_days_held"] < 8)
        ].copy()

    # Add ranks
    # new_grouped_df = add_ranks(new_grouped_df, "target_met_true", ascending=False)
    new_grouped_df = add_ranks(new_grouped_df, "median_days_held", ascending=True)
    new_grouped_df = add_ranks(new_grouped_df, "mean_days_held", ascending=True)
    new_grouped_df = add_ranks(new_grouped_df, "max_days_held", ascending=True)

    new_grouped_df["rank"] = (
        new_grouped_df["rank_target_met_true"]
        + new_grouped_df["rank_median_days_held"]
        + new_grouped_df["rank_mean_days_held"]
        + new_grouped_df["rank_max_days_held"]
    )

    idx = new_grouped_df.groupby("Strategy")["rank"].idxmin()
    top_ranked_df = new_grouped_df.loc[idx]

    # Generate snippets and check Days_Held condition
    snippets = []
    indices_to_remove = []

    for index, row in top_ranked_df.iterrows():
        param2 = "None" if pd.isnull(row["Param2"]) else repr(row["Param2"])
        param3 = "None" if pd.isnull(row["Param3"]) else repr(row["Param3"])
        query_str = (
            f'Strategy == "{row["Strategy"]}" & '
            f'Param1 == {row["Param1"]} & '
            f"Param2 == {param2} & "
            f"Param3 == {param3}"
        )
        snippets.append(query_str)

        filtered_df = raw_results_df.query(query_str)

        if (filtered_df["Days_Held"] > 16).sum() > 3:
            indices_to_remove.append(index)

    top_ranked_df = top_ranked_df.drop(indices_to_remove)

    snippets = []
    for index, row in top_ranked_df.iterrows():
        param2 = "None" if pd.isnull(row["Param2"]) else repr(row["Param2"])
        param3 = "None" if pd.isnull(row["Param3"]) else repr(row["Param3"])
        query_str = (
            f'Strategy == "{row["Strategy"]}" & '
            f'Param1 == {row["Param1"]} & '
            f"Param2 == {param2} & "
            f"Param3 == {param3}"
        )
        snippets.append(query_str)

    for query_str in snippets:
        print(query_str)
        print()

        raw_results_for_visual_df = raw_results_df.query(query_str).copy()
        raw_results_for_visual_df["ticker"] = ticker
        # print(raw_results_for_visual_df)

        old_raw_results_for_visual_df = pd.concat(
            [old_raw_results_for_visual_df, raw_results_for_visual_df],
            ignore_index=True,
        )

    old_raw_results_for_visual_df["Buy_Date"] = pd.to_datetime(
        old_raw_results_for_visual_df["Buy_Date"]
    )
    old_raw_results_for_visual_df["Sell_Date"] = pd.to_datetime(
        old_raw_results_for_visual_df["Sell_Date"]
    )

    daily_buy_df = (
        old_raw_results_for_visual_df.groupby("Buy_Date")
        .agg(
            ticker_count=("ticker", "size"),
            tickers=("ticker", lambda x: list(x)),
            strategies=("Strategy", lambda x: list(x)),
        )
        .reset_index()
    )

    old_raw_results_for_visual_df["Buy_Month"] = old_raw_results_for_visual_df[
        "Buy_Date"
    ].dt.to_period("M")
    monthly_buy_df = (
        old_raw_results_for_visual_df.groupby("Buy_Month")
        .agg(buy_count=("ticker", "size"))
        .reset_index()
    )

    old_raw_results_for_visual_df["Sell_Month"] = old_raw_results_for_visual_df[
        "Sell_Date"
    ].dt.to_period("M")
    # monthly_sell_df = (old_raw_results_for_visual_df[old_raw_results_for_visual_df['Days_Held'] <= 17]
    #                    .groupby('Sell_Month')
    #                    .agg(sell_count=('ticker', 'size'))
    #                    .reset_index())

    # Save the concatenated DataFrame to a CSV file
    # old_raw_results_for_visual_df.to_csv('old_raw_results_for_visual_df.csv', index=False)
    # files.download('old_raw_results_for_visual_df.csv')

    return (
        top_ranked_df,
        daily_buy_df,
        monthly_buy_df,
        old_raw_results_for_visual_df,
    )  # monthly_sell_df




# Function to process a single ticker
def process_ticker(ticker, all_raw_results_df, old_raw_results_for_visual_df):
    data = yf.download(ticker, start="2023-06-15", end="2024-07-01")

    results = []

    # Combine results into a single DataFrame
    raw_results_df = pd.concat(results, ignore_index=True)

    # Fill NaN values with a placeholder (e.g., 'None')
    raw_results_df.fillna("None", inplace=True)

    # Group by Strategy, Expected_Growth, and Param1, Param2, Param3 and calculate statistics
    grouped_df = (
        raw_results_df.groupby(
            ["Strategy", "Expected_Growth", "Param1", "Param2", "Param3"]
        )
        .agg(
            # mean_days_held=('Days_Held', 'mean'),
            # 2, 2, 2, 2, 30
            # mean 6.33
            #  std 3
            # mean + 3 * std = 13.33
            #  2 < 13.33 OK
            # 30 > 13.33 EXCLUDE
            mean_days_held=("Days_Held", mean_excluding_outliers),
            median_days_held=("Days_Held", "median"),
            total_rows=("Buy_Date", "size"),
            target_met_true=("Target_Met", "sum"),
            min_days_held=("Days_Held", "min"),
            max_days_held=("Days_Held", "max"),
        )
        .reset_index()
    )

    # Calculate percentage of Target_Met = True
    grouped_df["percent_target_met"] = (
        grouped_df["target_met_true"] / grouped_df["total_rows"] * 100
    )

    # Combine results into a single DataFrame
    raw_results_df = pd.concat(results, ignore_index=True)

    # Add ticker column
    raw_results_df["ticker"] = ticker

    # Append to all_raw_results_df
    all_raw_results_df = pd.concat(
        [all_raw_results_df, raw_results_df], ignore_index=True
    )

    # Fill NaN values with a placeholder (e.g., 'None')
    raw_results_df.fillna("None", inplace=True)

    # Process grouped data
    top_ranked_df, daily_buy_df, monthly_buy_df, old_raw_results_for_visual_df = (
        process_grouped_df(
            grouped_df, raw_results_df, ticker, old_raw_results_for_visual_df
        )
    )  # monthly_sell_df

    settings_for_server_df = top_ranked_df.copy()
    settings_for_server_df["ticker"] = ticker
    settings_for_server_df["stop_loss"] = 0.1
    settings_for_server_df["days_to_drop"] = (
        settings_for_server_df["mean_days_held"].round(0) * 2 + 2
    )
    settings_for_server_df.drop(
        columns=[
            "mean_days_held",
            "median_days_held",
            "target_met_true",
            "min_days_held",
            "max_days_held",
            "percent_target_met",
            "rank_target_met_true",
            "rank_median_days_held",
            "rank_mean_days_held",
            "rank_max_days_held",
            "rank",
        ],
        inplace=True,
    )

    return (
        settings_for_server_df,
        top_ranked_df,
        daily_buy_df,
        monthly_buy_df,
        all_raw_results_df,
        old_raw_results_for_visual_df,
    )  # monthly_sell_df,
