> This project is designed solely for educational purposes.

## setup

```bash
pip install -r requirements.txt
```

## usage

```python
import pandas as pd

url = 'https://raw.githubusercontent.com/mmiliukas/screeners/main/tickers.csv'
tickers = pd.read_csv(url)
```


## columns
```python
'''
 #   Column                         Non-Null Count  Dtype
---  ------                         --------------  -----
 0   Symbol                         1642 non-null   object
 1   Name                           1642 non-null   object
 2   Sector                         1642 non-null   object
 3   Industry                       1642 non-null   object
 4   ETF                            1642 non-null   object
 5   Winners 1                      1642 non-null   int64
 6   Winners 1 First Seen           331 non-null    object
 7   Winners 5                      1642 non-null   int64
 8   Winners 5 First Seen           299 non-null    object
 9   Winners 10                     1642 non-null   int64
 10  Winners 10 First Seen          197 non-null    object
 11  Winners 100                    1642 non-null   int64
 12  Winners 100 First Seen         60 non-null     object
 13  Loosers 1                      1642 non-null   int64
 14  Loosers 1 First Seen           446 non-null    object
 15  Loosers 5                      1642 non-null   int64
 16  Loosers 5 First Seen           172 non-null    object
 17  Loosers 10                     1642 non-null   int64
 18  Loosers 10 First Seen          59 non-null     object
 19  Loosers 100                    1642 non-null   int64
 20  Loosers 100 First Seen         240 non-null    object
 21  Random 1                       1642 non-null   int64
 22  Random 1 First Seen            68 non-null     object
 23  Random 5                       1642 non-null   int64
 24  Random 5 First Seen            97 non-null     object
 25  Random 10                      1642 non-null   int64
 26  Random 10 First Seen           114 non-null    object
 27  Random 100                     1642 non-null   int64
 28  Random 100 First Seen          161 non-null    object
 29  Screener                       1642 non-null   object
 30  Screener First Seen            1642 non-null   object
 31  Screener First Seen Close      1642 non-null   float64
 32  Financials Market Cap          1624 non-null   float64
 33  Financials Total Cash          1636 non-null   float64
 34  Financials Total Debt          1406 non-null   float64
 35  Financials Quick Ratio         1642 non-null   float64
 36  Financials Current Ratio       1642 non-null   float64
 37  Financials Total Revenue       1317 non-null   float64
 38  Financials Debt To Equity      1239 non-null   float64
 39  Financials Return On Assets    1588 non-null   float64
 40  Financials Return On Equity    1448 non-null   float64
 41  Financials Free Cashflow       1529 non-null   float64
 42  Financials Operating Cashflow  1595 non-null   float64
'''
```
