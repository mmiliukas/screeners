## setup

```bash
python -m pip install -r requirements.txt
```

## config

```yaml
on:
  schedule:
    - cron: '0 8 * * *'
```

## usage

```python
import pandas as pd

base_url = 'https://raw.githubusercontent.com/mmiliukas/screeners/main'
all = pd.read_csv(f'{base_url}/runs/all.csv', parse_dates=['Date'])

'''
 #   Column             Non-Null Count  Dtype
---  ------             --------------  -----
 0   Symbol             1025 non-null   object
 1   Name               1025 non-null   object
 2   Price (Intraday)   1025 non-null   float64
 3   Change             1025 non-null   float64
 4   % Change           1025 non-null   float64
 5   Volume             1025 non-null   int64
 6   Avg Vol (3 month)  1025 non-null   int64
 7   Market Cap         1025 non-null   int64
 8   Date               1025 non-null   datetime64[ns]
 '''

#  get unique symbols
all['Symbol'].unique()


# sorty by % Change
all.sort_values(by=['% Change'], ascending=False)[['Symbol', '% Change']]

'''
    Symbol  % Change
386   PSCO    550.00
83    PSCO    550.00
145   PSCO    550.00
610   PSCO    550.00
763   PSCO    550.00
..     ...       ...
248   EKSN      0.00
393   EKSN      0.00
131  RTMFF      0.00
244  TLSIW     -7.69
915   BYSD    -22.76
'''

# filter rows by condition
all[all['% Change'] > 50]

'''
     Symbol                          Name  ...  Market Cap                       Date
4     KROEF                       KR1 Plc  ...   203975000 2023-12-08 19:07:18.414773
11     EXOD         Exodus Movement, Inc.  ...           0 2023-12-08 19:07:18.414773
29     TNRG  Thunder Energies Corporation  ...     7872000 2023-12-08 19:07:22.287810
36    OLVRF         Olivut Resources Ltd.  ...     5156000 2023-12-08 19:07:22.287810
43    CPPMF         COPPERNICO METALS INC  ...           0 2023-12-08 19:07:22.287810
...     ...                           ...  ...         ...                        ...
991   GXUSF     Guardian Exploration Inc.  ...    24501000 2023-12-08 22:08:15.541271
995    TNRG  Thunder Energies Corporation  ...     7872000 2023-12-08 22:08:15.541271
1001  OLVRF         Olivut Resources Ltd.  ...     5156000 2023-12-08 22:08:15.541271
1007  CPPMF         COPPERNICO METALS INC  ...           0 2023-12-08 22:08:15.541271
1015  KROEF                       KR1 Plc  ...   203975000 2023-12-09 08:10:19.965670
'''

>>> tickers = pd.read_json('https://raw.githubusercontent.com/mmiliukas/screeners/main/tickers.json')

>>> all
    Symbol                               Name  Price (Intraday)  ...  Avg Vol (3 month)  Market Cap                        Date
0    SAMHF                  Alleima AB (publ)            7.3000  ...                  1  2270000000  2023-12-08T19:07:18.414773
1     BITF                      Bitfarms Ltd.            2.5050  ...           12576000   808116000  2023-12-08T19:07:18.414773
2     APLD        Applied Digital Corporation            6.2600  ...            3361000   665831000  2023-12-08T19:07:18.414773
3     APLT         Applied Therapeutics, Inc.            3.2150  ...            1039000   248292000  2023-12-08T19:07:18.414773
4    KROEF                            KR1 Plc            1.1500  ...               8687   203975000  2023-12-08T19:07:18.414773
..     ...                                ...               ...  ...                ...         ...                         ...
339  EATBF  Eat & Beyond Global Holdings Inc.            0.0645  ...               3933     1539000  2023-12-08T17:29:07.448884
340   MHHC              MHHC Enterprises Inc.            0.0999  ...              22499    91702000  2023-12-08T17:29:07.448884
341  MNRLD            Badlands Resources Inc.            0.3700  ...               8663           0  2023-12-08T17:29:07.448884
342  CPPMF              COPPERNICO METALS INC            0.0750  ...              76242           0  2023-12-08T17:29:07.448884
343   NREG                     NewRegen, Inc.            0.0230  ...            1224000           0  2023-12-08T17:29:07.448884

[344 rows x 9 columns]

>>> tickers

                        address1       city      zip  ... fiveYearAvgDividendYield earningsGrowth pegRatio
0                    Storgatan 2  Sandviken   811 81  ...                      NaN            NaN      NaN
1            18 King Street East    Toronto  M5C 1C4  ...                      NaN            NaN      NaN
2    3811 Turtle Creek Boulevard     Dallas    75219  ...                      NaN            NaN      NaN
3                 545 5th Avenue   New York    10017  ...                      NaN            NaN      NaN
4              First Names House    Douglas  IM2 4DF  ...                      NaN            NaN      NaN
..                           ...        ...      ...  ...                      ...            ...      ...
339    1570 – 505 Burrard Street  Vancouver  V7X 1M5  ...                      NaN            NaN      NaN
340          400 Union Avenue SE    Olympia    98501  ...                      NaN            NaN      NaN
341           200 Burrard Street  Vancouver  V6C 3L6  ...                      NaN            NaN      NaN
342                          NaN        NaN      NaN  ...                      NaN            NaN      NaN
343     200 Ashford Center North    Atlanta    30338  ...                      NaN            NaN      NaN

[344 rows x 134 columns]
```
