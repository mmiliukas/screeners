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
 0   Symbol                         1175 non-null   object
 1   Name                           1175 non-null   object
 2   Sector                         1175 non-null   object
 3   Industry                       1175 non-null   object
 4   ETF                            1175 non-null   object
 5   Winners                        1175 non-null   int64
 6   Winners First Seen             506 non-null    object
 7   Loosers                        1175 non-null   int64
 8   Loosers First Seen             613 non-null    object
 9   Random                         1175 non-null   int64
 10  Random First Seen              171 non-null    object
 11  Random 5                       1175 non-null   int64
 12  Random 5 First Seen            68 non-null     object
 13  Random 10                      1175 non-null   int64
 14  Random 10 First Seen           72 non-null     object
 15  Screener                       1175 non-null   object
 16  Screener First Seen            1175 non-null   object
 17  Financials Market Cap          1156 non-null   float64
 18  Financials Total Cash          1167 non-null   float64
 19  Financials Total Debt          980 non-null    float64
 20  Financials Quick Ratio         1175 non-null   float64
 21  Financials Current Ratio       1175 non-null   float64
 22  Financials Total Revenue       887 non-null    float64
 23  Financials Debt To Equity      844 non-null    float64
 24  Financials Return On Assets    1121 non-null   float64
 25  Financials Return On Equity    996 non-null    float64
 26  Financials Free Cashflow       1051 non-null   float64
 27  Financials Operating Cashflow  1115 non-null   float64
 28  Screener First Seen Close      1172 non-null   float64
'''
```