import glob
import os

import pandas as pd


def top_1():
    paths = glob.glob("./top-1/*.csv") + glob.glob("./top-1-5/*.csv")

    all = []

    for path in paths:
        basename = os.path.basename(path)
        only_name = os.path.splitext(basename)[0]

        # split into at most 4 parts (year, month, day, suffix?)
        parts = only_name.split("-", 3)

        df = pd.read_csv(path)

        screener = ("Winners" if len(parts) == 3 else parts[3]).capitalize()

        if screener.startswith("5"):
            if screener == "5":
                screener = "Winners 5"
            else:
                screener = screener.replace("5-", "").capitalize() + " 5"
        else:
            screener = screener + " 10"

        df["Screener"] = screener

        df["Date"] = f"{parts[0]}-{parts[1]}-{parts[2]}"
        df["Date"] = pd.to_datetime(df["Date"]).dt.date

        df["Order"] = df.index + 1

        all.append(df)

    result = pd.concat(all)
    assert isinstance(result, pd.DataFrame)

    result = result.sort_values(by=["Date", "Screener", "Order"])
    result.to_csv("tickers-top-1.csv", index=False)
