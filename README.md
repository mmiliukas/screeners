> This project is designed solely for educational purposes.

## setup

```bash
pip install -r requirements.txt
```

## config

Expression can be checked online at [https://crontab.cronhub.io](https://crontab.cronhub.io)

```yaml
on:
  schedule:
    - cron: '0 6 * * 2-6'
```

## usage

```python
import pandas as pd

base_url = 'https://raw.githubusercontent.com/mmiliukas/screeners/main'

tickers = pd.read_csv(f'{base_url}/tickers.csv', parse_dates=['Date'])
```

### results

```python
'''
TODO:
'''
````