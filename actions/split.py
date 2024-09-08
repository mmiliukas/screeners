import glob

import pandas as pd
from tqdm import tqdm


def __split_screener(
    from_dir: str, range_ex: tuple[int, int], range_in: tuple[int, int]
) -> pd.DataFrame:
    names = glob.glob(f"runs/{from_dir}/*.csv")
    results = []

    with tqdm(total=len(names)) as progress:
        for name in names:
            df = pd.read_csv(name)

            df_ex = df[df["Price (Intraday)"].between(range_ex[0], range_ex[1])]
            df_in = df[df["Price (Intraday)"].between(range_in[0], range_in[1])]

            df_in.to_csv(name, index=False)
            results.append(df_ex)

            progress.update(1)

    return pd.concat([result for result in results if not result.empty])


def split() -> None:
    # df = split("winners100", (10, 30), (30, 100))
    # df.to_csv("./runs/winners30/2024_08_15_01_01_01.csv", index=False)

    # df = split("winners100", (30, 50), (50, 100))
    # df.to_csv("./runs/winners50/2024_08_15_01_01_01.csv", index=False)

    # df = split("winners100", (50, 70), (70, 100))
    # df.to_csv("./runs/winners70/2024_08_15_01_01_01.csv", index=False)

    # df = split("loosers100", (10, 30), (30, 100))
    # df.to_csv("./runs/loosers30/2024_08_15_01_01_01.csv", index=False)

    # df = split("loosers100", (30, 50), (50, 100))
    # df.to_csv("./runs/loosers50/2024_08_15_01_01_01.csv", index=False)

    # df = split("loosers100", (50, 70), (70, 100))
    # df.to_csv("./runs/loosers70/2024_08_15_01_01_01.csv", index=False)

    df = __split_screener("random100", (10, 30), (30, 100))
    df.to_csv("./runs/random30/2024_08_15_01_01_01.csv", index=False)

    df = __split_screener("random100", (30, 50), (50, 100))
    df.to_csv("./runs/random50/2024_08_15_01_01_01.csv", index=False)

    df = __split_screener("random100", (50, 70), (70, 100))
    df.to_csv("./runs/random70/2024_08_15_01_01_01.csv", index=False)
