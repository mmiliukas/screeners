import yaml

from datetime import timedelta
from requests_cache import CachedSession

from .config import config

# https://requests-cache.readthedocs.io/en/stable/user_guide.html
session = CachedSession(config['yfinance']['cache_name'],
                        backend=config['yfinance']['backend'],
                        expire_after=timedelta(days=config['yfinance']['expire_after_days']))
