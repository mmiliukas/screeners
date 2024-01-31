import glob
import pandas as pd

def aggregate(source: str, target: str):
    all = glob.glob(source)
    df = pd.concat((pd.read_csv(file) for file in all), ignore_index=True)
    df.to_csv(target, index=False)

if __name__ == '__main__':
    aggregate('./runs/*.csv', './all.csv')
    aggregate('./runs-loosers/*.csv', './all-loosers.csv')
    aggregate('./runs-random/*.csv', './all-random.csv')
