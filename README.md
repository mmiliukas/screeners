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
RangeIndex: 1039 entries, 0 to 1038
Data columns (total 26 columns):
 #   Column                       Non-Null Count  Dtype
---  ------                       --------------  -----
 0   Symbol                       1039 non-null   object
 1   Name                         1034 non-null   object
 2   Sector                       1028 non-null   object
 3   Industry                     1028 non-null   object
 4   ETF                          1028 non-null   object
 5   Winners                      1039 non-null   int64
 6   Loosers                      1039 non-null   int64
 7   Random                       1039 non-null   int64
 8   Screener                     1039 non-null   object
 9   FinancialsCurrentPrice       1039 non-null   float64
 10  FinancialsMarketCap          998 non-null    float64
 11  FinancialsVolume             1037 non-null   float64
 12  FinancialsAverageVolume      1039 non-null   int64
 13  FinancialsTotalCash          1031 non-null   float64
 14  FinancialsTotalDebt          853 non-null    float64
 15  FinancialsQuickRatio         1039 non-null   float64
 16  FinancialsCurrentRatio       1039 non-null   float64
 17  FinancialsTotalRevenue       781 non-null    float64
 18  FinancialsDebtToEquity       711 non-null    float64
 19  FinancialsReturnOnAssets     974 non-null    float64
 20  FinancialsReturnOnEquity     853 non-null    float64
 21  FinancialsFreeCashflow       916 non-null    float64
 22  FinancialsOperatingCashflow  989 non-null    float64
 23  CurrentRatio                 943 non-null    float64
 24  QuickRatio                   431 non-null    float64
 25  CashRatio                    940 non-null    float64
dtypes: float64(16), int64(4), object(6)
'''
```