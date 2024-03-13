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
Data columns (total 22 columns):
 #   Column                         Non-Null Count  Dtype
---  ------                         --------------  -----
 0   Symbol                         1062 non-null   object
 1   Name                           1056 non-null   object
 2   Sector                         1062 non-null   object
 3   Industry                       1062 non-null   object
 4   ETF                            1062 non-null   object
 5   Winners                        1062 non-null   int64
 6   Loosers                        1062 non-null   int64
 7   Random                         1062 non-null   int64
 8   Random 5                       1062 non-null   int64
 9   Random 10                      1062 non-null   int64
 10  Screener                       1062 non-null   object
 11  Financials Market Cap          1024 non-null   float64
 12  Financials Total Cash          1055 non-null   float64
 13  Financials Total Debt          874 non-null    float64
 14  Financials Quick Ratio         1062 non-null   float64
 15  Financials Current Ratio       1062 non-null   float64
 16  Financials Total Revenue       802 non-null    float64
 17  Financials Debt To Equity      733 non-null    float64
 18  Financials Return On Assets    994 non-null    float64
 19  Financials Return On Equity    875 non-null    float64
 20  Financials Free Cashflow       932 non-null    float64
 21  Financials Operating Cashflow  1008 non-null   float64
dtypes: float64(11), int64(5), object(6)
'''
```