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
RangeIndex: 6127 entries, 0 to 6126
Data columns (total 30 columns):
 #   Column                       Non-Null Count  Dtype
---  ------                       --------------  -----
 0   Symbol                       6127 non-null   object
 1   Name                         6123 non-null   object
 2   Price (Intraday)             6127 non-null   float64
 3   Change                       6127 non-null   float64
 4   % Change                     6127 non-null   float64
 5   Volume                       6127 non-null   int64
 6   Avg Vol (3 month)            6127 non-null   int64
 7   Market Cap                   6127 non-null   int64
 8   Date                         6127 non-null   object
 9   Screener                     6127 non-null   object
 10  Sector                       5989 non-null   object
 11  Industry                     5989 non-null   object
 12  ETF                          5989 non-null   object
 13  FinancialsCurrentPrice       6042 non-null   float64
 14  FinancialsMarketCap          5790 non-null   float64
 15  FinancialsVolume             6125 non-null   float64
 16  FinancialsAverageVolume      6126 non-null   float64
 17  FinancialsTotalCash          5729 non-null   float64
 18  FinancialsTotalDebt          4945 non-null   float64
 19  FinancialsQuickRatio         5595 non-null   float64
 20  FinancialsCurrentRatio       5668 non-null   float64
 21  FinancialsTotalRevenue       4615 non-null   float64
 22  FinancialsDebtToEquity       3498 non-null   float64
 23  FinancialsReturnOnAssets     5469 non-null   float64
 24  FinancialsReturnOnEquity     4306 non-null   float64
 25  FinancialsFreeCashflow       5112 non-null   float64
 26  FinancialsOperatingCashflow  5555 non-null   float64
 27  CurrentRatio                 6122 non-null   float64
 28  QuickRatio                   6012 non-null   float64
 29  CashRatio                    6119 non-null   float64
'''
```