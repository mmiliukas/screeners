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


                                                                 Symbol
Sector                 Industry                                        
Basic Materials        Agricultural Inputs                           11
                       Building Materials                             1
                       Chemicals                                      8
                       Coking Coal                                    3
                       Copper                                        13
                       Gold                                         269
                       Lumber & Wood Production                       3
                       Other Industrial Metals & Mining             258
                       Other Precious Metals & Mining                50
                       Silver                                         8
                       Specialty Chemicals                           59
                       Steel                                          8
Communication Services Advertising Agencies                          78
                       Broadcasting                                  17
                       Electronic Gaming & Multimedia                16
                       Entertainment                                 38
                       Internet Content & Information                71
                       Publishing                                     1
                       Telecom Services                              40
Consumer Cyclical      Apparel Manufacturing                         27
                       Apparel Retail                                25
                       Auto & Truck Dealerships                      14
                       Auto Manufacturers                            41
                       Auto Parts                                    11
                       Department Stores                             20
                       Footwear & Accessories                         1
                       Furnishings, Fixtures & Appliances            19
                       Gambling                                      24
                       Internet Retail                               17
                       Leisure                                       20
                       Lodging                                        2
                       Luxury Goods                                   3
                       Packaging & Containers                         3
                       Personal Services                              5
                       Recreational Vehicles                          2
                       Residential Construction                       1
                       Resorts & Casinos                              2
                       Restaurants                                    8
                       Specialty Retail                              25
                       Travel Services                                3
Consumer Defensive     Beverages - Non-Alcoholic                     20
                       Beverages - Wineries & Distilleries            8
                       Beverages—Wineries & Distilleries              1
                       Discount Stores                                1
                       Education & Training Services                 30
                       Farm Products                                 15
                       Food Distribution                             25
                       Grocery Stores                                 8
                       Household & Personal Products                 46
                       Packaged Foods                               113
                       Tobacco                                       41
Energy                 Oil & Gas E&P                                 81
                       Oil & Gas Equipment & Services                16
                       Oil & Gas Integrated                           2
                       Oil & Gas Midstream                           28
                       Oil & Gas Refining & Marketing                34
                       Thermal Coal                                   1
                       Uranium                                      164
Financial Services     Asset Management                              40
                       Banks - Regional                              85
                       Capital Markets                              302
                       Credit Services                               64
                       Insurance - Diversified                        3
                       Insurance - Property & Casualty                1
                       Insurance - Specialty                          1
                       Insurance Brokers                              5
                       Mortgage Finance                              21
                       Shell Companies                              183
Healthcare             Biotechnology                                612
                       Diagnostics & Research                        32
                       Drug Manufacturers - General                   2
                       Drug Manufacturers - Specialty & Generic     247
                       Health Information Services                   68
                       Healthcare Plans                               2
                       Medical Care Facilities                       37
                       Medical Devices                              127
                       Medical Distribution                          16
                       Medical Instruments & Supplies                63
                       Pharmaceutical Retailers                      18
Industrials            Aerospace & Defense                           53
                       Airlines                                      18
                       Building Products & Equipment                 12
                       Conglomerates                                 23
                       Consulting Services                            7
                       Electrical Equipment & Parts                  77
                       Engineering & Construction                    76
                       Farm & Heavy Construction Machinery           21
                       Industrial Distribution                        3
                       Integrated Freight & Logistics                 1
                       Marine Shipping                               11
                       Metal Fabrication                              6
                       Pollution & Treatment Controls                17
                       Railroads                                      6
                       Rental & Leasing Services                     36
                       Security & Protection Services                43
                       Specialty Business Services                   27
                       Specialty Industrial Machinery                45
                       Staffing & Employment Services                 4
                       Tools & Accessories                            1
                       Trucking                                      14
                       Waste Management                              20
Real Estate            REIT - Diversified                             3
                       REIT - Healthcare Facilities                   3
                       REIT - Mortgage                                4
                       REIT - Office                                  5
                       REIT - Specialty                              11
                       Real Estate - Development                     35
                       Real Estate - Diversified                     13
                       Real Estate Services                          76
Technology             Communication Equipment                       26
                       Computer Hardware                             37
                       Consumer Electronics                          16
                       Electronic Components                         34
                       Electronics & Computer Distribution           31
                       Information Technology Services               81
                       Scientific & Technical Instruments            50
                       Semiconductors                                52
                       Software - Application                       370
                       Software - Infrastructure                    158
                       Software—Application                           1
                       Solar                                         24
Utilities              Utilities - Independent Power Producers        2
                       Utilities - Regulated Water                    7
                       Utilities - Renewable                         18
```python
'''
                                                                 Symbol
Sector                 Industry                                        
Basic Materials        Agricultural Inputs                           11
                       Building Materials                             1
                       Chemicals                                      8
                       Coking Coal                                    3
                       Copper                                        13
                       Gold                                         269
                       Lumber & Wood Production                       3
                       Other Industrial Metals & Mining             258
                       Other Precious Metals & Mining                50
                       Silver                                         8
                       Specialty Chemicals                           59
                       Steel                                          8
Communication Services Advertising Agencies                          78
                       Broadcasting                                  17
                       Electronic Gaming & Multimedia                16
                       Entertainment                                 38
                       Internet Content & Information                71
                       Publishing                                     1
                       Telecom Services                              40
Consumer Cyclical      Apparel Manufacturing                         27
                       Apparel Retail                                25
                       Auto & Truck Dealerships                      14
                       Auto Manufacturers                            41
                       Auto Parts                                    11
                       Department Stores                             20
                       Footwear & Accessories                         1
                       Furnishings, Fixtures & Appliances            19
                       Gambling                                      24
                       Internet Retail                               17
                       Leisure                                       20
                       Lodging                                        2
                       Luxury Goods                                   3
                       Packaging & Containers                         3
                       Personal Services                              5
                       Recreational Vehicles                          2
                       Residential Construction                       1
                       Resorts & Casinos                              2
                       Restaurants                                    8
                       Specialty Retail                              25
                       Travel Services                                3
Consumer Defensive     Beverages - Non-Alcoholic                     20
                       Beverages - Wineries & Distilleries            8
                       Beverages—Wineries & Distilleries              1
                       Discount Stores                                1
                       Education & Training Services                 30
                       Farm Products                                 15
                       Food Distribution                             25
                       Grocery Stores                                 8
                       Household & Personal Products                 46
                       Packaged Foods                               113
                       Tobacco                                       41
Energy                 Oil & Gas E&P                                 81
                       Oil & Gas Equipment & Services                16
                       Oil & Gas Integrated                           2
                       Oil & Gas Midstream                           28
                       Oil & Gas Refining & Marketing                34
                       Thermal Coal                                   1
                       Uranium                                      164
Financial Services     Asset Management                              40
                       Banks - Regional                              85
                       Capital Markets                              302
                       Credit Services                               64
                       Insurance - Diversified                        3
                       Insurance - Property & Casualty                1
                       Insurance - Specialty                          1
                       Insurance Brokers                              5
                       Mortgage Finance                              21
                       Shell Companies                              183
Healthcare             Biotechnology                                612
                       Diagnostics & Research                        32
                       Drug Manufacturers - General                   2
                       Drug Manufacturers - Specialty & Generic     247
                       Health Information Services                   68
                       Healthcare Plans                               2
                       Medical Care Facilities                       37
                       Medical Devices                              127
                       Medical Distribution                          16
                       Medical Instruments & Supplies                63
                       Pharmaceutical Retailers                      18
Industrials            Aerospace & Defense                           53
                       Airlines                                      18
                       Building Products & Equipment                 12
                       Conglomerates                                 23
                       Consulting Services                            7
                       Electrical Equipment & Parts                  77
                       Engineering & Construction                    76
                       Farm & Heavy Construction Machinery           21
                       Industrial Distribution                        3
                       Integrated Freight & Logistics                 1
                       Marine Shipping                               11
                       Metal Fabrication                              6
                       Pollution & Treatment Controls                17
                       Railroads                                      6
                       Rental & Leasing Services                     36
                       Security & Protection Services                43
                       Specialty Business Services                   27
                       Specialty Industrial Machinery                45
                       Staffing & Employment Services                 4
                       Tools & Accessories                            1
                       Trucking                                      14
                       Waste Management                              20
Real Estate            REIT - Diversified                             3
                       REIT - Healthcare Facilities                   3
                       REIT - Mortgage                                4
                       REIT - Office                                  5
                       REIT - Specialty                              11
                       Real Estate - Development                     35
                       Real Estate - Diversified                     13
                       Real Estate Services                          76
Technology             Communication Equipment                       26
                       Computer Hardware                             37
                       Consumer Electronics                          16
                       Electronic Components                         34
                       Electronics & Computer Distribution           31
                       Information Technology Services               81
                       Scientific & Technical Instruments            50
                       Semiconductors                                52
                       Software - Application                       370
                       Software - Infrastructure                    158
                       Software—Application                           1
                       Solar                                         24
Utilities              Utilities - Independent Power Producers        2
                       Utilities - Regulated Water                    7
                       Utilities - Renewable                         18'''
```