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
 0   Symbol                         1343 non-null   object
 1   Name                           1343 non-null   object
 2   Sector                         1343 non-null   object
 3   Industry                       1343 non-null   object
 4   ETF                            1343 non-null   object
 5   Winners                        1343 non-null   int64
 6   Winners First Seen             508 non-null    object
 7   Winners 1                      1343 non-null   int64
 8   Winners 1 First Seen           37 non-null     object
 9   Winners 5                      1343 non-null   int64
 10  Winners 5 First Seen           12 non-null     object
 11  Winners 10                     1343 non-null   int64
 12  Winners 10 First Seen          6 non-null      object
 13  Winners 100                    1343 non-null   int64
 14  Winners 100 First Seen         7 non-null      object
 15  Loosers                        1343 non-null   int64
 16  Loosers First Seen             594 non-null    object
 17  Loosers 1                      1343 non-null   int64
 18  Loosers 1 First Seen           23 non-null     object
 19  Loosers 5                      1343 non-null   int64
 20  Loosers 5 First Seen           3 non-null      object
 21  Loosers 10                     1343 non-null   int64
 22  Loosers 10 First Seen          4 non-null      object
 23  Loosers 100                    1343 non-null   int64
 24  Loosers 100 First Seen         58 non-null     object
 25  Random                         1343 non-null   int64
 26  Random First Seen              170 non-null    object
 27  Random 1                       1343 non-null   int64
 28  Random 1 First Seen            29 non-null     object
 29  Random 5                       1343 non-null   int64
 30  Random 5 First Seen            70 non-null     object
 31  Random 10                      1343 non-null   int64
 32  Random 10 First Seen           76 non-null     object
 33  Random 100                     1343 non-null   int64
 34  Random 100 First Seen          110 non-null    object
 35  Screener                       1343 non-null   object
 36  Screener First Seen            1343 non-null   object
 37  Screener First Seen Close      1343 non-null   float64
 38  Financials Market Cap          1324 non-null   float64
 39  Financials Total Cash          1336 non-null   float64
 40  Financials Total Debt          1138 non-null   float64
 41  Financials Quick Ratio         1343 non-null   float64
 42  Financials Current Ratio       1343 non-null   float64
 43  Financials Total Revenue       1049 non-null   float64
 44  Financials Debt To Equity      994 non-null    float64
 45  Financials Return On Assets    1291 non-null   float64
 46  Financials Return On Equity    1156 non-null   float64
 47  Financials Free Cashflow       1218 non-null   float64
 48  Financials Operating Cashflow  1280 non-null   float64
'''
```