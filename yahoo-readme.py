import pandas as pd

if __name__ == '__main__':
  df = pd.read_csv('tickers.csv')
  df = df[['Sector', 'Industry', 'Symbol']].groupby(by=['Sector', 'Industry']).count()
  df.to_string()

  with open('README.md', 'r') as file:
    content = file.read()
    content = content.split(sep='## results')[0]
    content = content + "\n```python\n'''\n" + df.to_string() + "'''\n```"

  with open('README.md', 'w') as file:
    file.write(content)
