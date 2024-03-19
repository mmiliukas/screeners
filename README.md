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
 0   Symbol                         1106 non-null   object
 1   Name                           1106 non-null   object
 2   Sector                         1106 non-null   object
 3   Industry                       1106 non-null   object
 4   ETF                            1106 non-null   object
 5   Winners                        1106 non-null   int64
 6   Winners First Seen             431 non-null    object
 7   Loosers                        1106 non-null   int64
 8   Loosers First Seen             614 non-null    object
 9   Random                         1106 non-null   int64
 10  Random First Seen              167 non-null    object
 11  Random 5                       1106 non-null   int64
 12  Random 5 First Seen            50 non-null     object
 13  Random 10                      1106 non-null   int64
 14  Random 10 First Seen           54 non-null     object
 15  Screener                       1106 non-null   object
 16  Screener First Seen            1106 non-null   object
 17  Financials Market Cap          1067 non-null   float64
 18  Financials Total Cash          1099 non-null   float64
 19  Financials Total Debt          911 non-null    float64
 20  Financials Quick Ratio         1106 non-null   float64
 21  Financials Current Ratio       1106 non-null   float64
 22  Financials Total Revenue       833 non-null    float64
 23  Financials Debt To Equity      768 non-null    float64
 24  Financials Return On Assets    1035 non-null   float64
 25  Financials Return On Equity    912 non-null    float64
 26  Financials Free Cashflow       968 non-null    float64
 27  Financials Operating Cashflow  1048 non-null   float64
'''
```