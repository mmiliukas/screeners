import glob
import pandas

if __name__ == '__main__':
    all_files = glob.glob('./runs/*.csv')
    df = pandas.concat((pandas.read_csv(file) for file in all_files), ignore_index=True)
    df.to_csv('./all.csv', index=False)
