import glob
import pandas as pd

if __name__ == '__main__':
    all_gainers = glob.glob('./runs/*.csv')
    df = pd.concat((pd.read_csv(file) for file in all_gainers), ignore_index=True)
    df.to_csv('./all.csv', index=False)

    all_loosers = glob.glob('./runs-loosers/*.csv')
    df = pd.concat((pd.read_csv(file) for file in all_loosers), ignore_index=True)
    df.to_csv('./all-loosers.csv', index=False)
