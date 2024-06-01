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