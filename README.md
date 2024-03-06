> This project is designed solely for educational purposes.

## setup

```bash
pip install -r requirements.txt
```

## usage

```python
import pandas as pd

url = 'https://raw.githubusercontent.com/mmiliukas/screeners/main/tickers.csv'
tickers = pd.read_csv(url, parse_dates=['Date'])
```


## columns
```python
'''
Data columns (total 13 columns):
 #   Column             Non-Null Count  Dtype
---  ------             --------------  -----
 0   Symbol             5679 non-null   object
 1   Name               5675 non-null   object
 2   Price (Intraday)   5679 non-null   float64
 3   Change             5679 non-null   float64
 4   % Change           5679 non-null   float64
 5   Volume             5679 non-null   int64
 6   Avg Vol (3 month)  5679 non-null   int64
 7   Market Cap         5679 non-null   int64
 8   Date               5679 non-null   object
 9   Screener           5679 non-null   object
 10  Sector             5505 non-null   object
 11  Industry           5505 non-null   object
 12  ETF                5505 non-null   object
'''
```