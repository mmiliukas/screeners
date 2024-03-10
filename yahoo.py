import sys
import asyncio

from screeners.config import config
from screeners.utils import retry
from screeners.scraper import scrape_screener, scrape_etfs

if __name__ == '__main__':

  username, password, cookies = sys.argv[1:]
  retry_times = config['scraper']['retry_times']

  retry(retry_times)(lambda: asyncio.run(scrape_etfs(
    username, password, cookies)))

  for screener in config['screeners']:

    screener_cache_name = screener['cache_name']
    screener_urls = screener['urls']

    retry(retry_times)(lambda: asyncio.run(scrape_screener(
      username, password, cookies, screener_cache_name, screener_urls)))
