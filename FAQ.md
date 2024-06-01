# FAQ

## What does +/- signs mean ?

+/- sign identifies increase and/or decrease of a metric from a previous run.
Runs can happen multiple times per day/hour/minute. Each time it's a diff/delta from a previous run.

## What does +/- next to stock/ticker symbol means ?

+/- sign next to stock/ticker identifies if ticker was added or removed to a group.
In example below we see that `1` one ticker `VJET` was removed from a `Loosers 1` group.

```
Loosers 1    456  -1         -VJET
```

## When screeners are scraped ?

The regular trading hours for the U.S. stock market,
which includes the Nasdaq Stock Market (Nasdaq)
and the New York Stock Exchange (NYSE),
are 9:30 am to 4 pm, except on stock market holidays.

Time difference between UTC and EST (-5 hours) and EDT (-4 hours):

```yaml
  schedule:
    # 09:00 in local time (in the morning)
    - cron: '0 6 * * *'
    # 16:30 in local time (market opened)
    - cron: '30 13 * * 1-5'
    # 23:00 in local time (market closed)
    - cron: '0 20 * * 1-5'
```

## Exchanges
The values of the exchange property in your ticker information from Yahoo Finance represent different stock exchanges where the respective securities are listed. Here's a brief explanation of each code:

- **ASE**: American Stock Exchange (now known as NYSE American)
- **BTS**: BTS Group Holdings (a Thai company, but this may need context as it's less common as an exchange code)
- **FRA**: Frankfurt Stock Exchange (Frankfurter Wertpapierbörse)
- **NAS**: NASDAQ Stock Market
- **NCM**: NASDAQ Capital Market
- **NGM**: NASDAQ Global Market
- **NMS**: NASDAQ Global Select Market
- **NYQ**: New York Stock Exchange (NYSE)
- **PCX**: Pacific Exchange (now part of NYSE Arca)
- **PNK**: Pink Sheets (over-the-counter trading of stocks not listed on a major exchange)

