#!/usr/bin/env python

import glob
import sys

import pandas as pd


def migrate(from_dir: str, to_dirs: list[str]):
    names = glob.glob(f"runs/{from_dir}/*.csv")
    df = pd.concat([pd.read_csv(name) for name in names])

    df_1 = df[df["Price (Intraday)"] <= 1]
    df_5 = df[(df["Price (Intraday)"] >= 1) & (df["Price (Intraday)"] <= 5)]
    df_10 = df[(df["Price (Intraday)"] >= 5) & (df["Price (Intraday)"] <= 10)]
    df_100 = df[df["Price (Intraday)"] >= 10]

    df_1.to_csv(f"runs/{to_dirs[0]}/2024_05_18_01_01_01.csv", index=False)
    df_5.to_csv(f"runs/{to_dirs[1]}/2024_05_18_01_01_01.csv", index=False)
    df_10.to_csv(f"runs/{to_dirs[2]}/2024_05_18_01_01_01.csv", index=False)
    df_100.to_csv(f"runs/{to_dirs[3]}/2024_05_18_01_01_01.csv", index=False)


def main(name: str):
    migrate(name, [f"{name}1", f"{name}5", f"{name}10", f"{name}100"])


if __name__ == "__main__":
    main(sys.argv[1])
