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
RangeIndex: 5973 entries, 0 to 5972
Data columns (total 27 columns):
 #   Column                       Non-Null Count  Dtype
---  ------                       --------------  -----
 0   Symbol                       5973 non-null   object
 1   Name                         5969 non-null   object
 2   Price (Intraday)             5973 non-null   float64
 3   Change                       5973 non-null   float64
 4   % Change                     5973 non-null   float64
 5   Volume                       5973 non-null   int64
 6   Avg Vol (3 month)            5973 non-null   int64
 7   Market Cap                   5973 non-null   int64
 8   Date                         5973 non-null   object
 9   Screener                     5973 non-null   object
 10  Sector                       5840 non-null   object
 11  Industry                     5840 non-null   object
 12  ETF                          5840 non-null   object
 13  FinancialsCurrentPrice       5890 non-null   float64
 14  FinancialsMarketCap          5644 non-null   float64
 15  FinancialsVolume             5971 non-null   float64
 16  FinancialsAverageVolume      5972 non-null   float64
 17  FinancialsTotalCash          5586 non-null   float64
 18  FinancialsTotalDebt          4822 non-null   float64
 19  FinancialsQuickRatio         5451 non-null   float64
 20  FinancialsCurrentRatio       5524 non-null   float64
 21  FinancialsTotalRevenue       4493 non-null   float64
 22  FinancialsDebtToEquity       3400 non-null   float64
 23  FinancialsReturnOnAssets     5333 non-null   float64
 24  FinancialsReturnOnEquity     4188 non-null   float64
 25  FinancialsFreeCashflow       4985 non-null   float64
 26  FinancialsOperatingCashflow  5416 non-null   float64
'''
```