import glob

import pandas as pd
from tqdm import tqdm


def split(
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
