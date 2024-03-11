import sys
import yaml
import json
import base64
import logging
import logging.config

from playwright.sync_api import sync_playwright

from screeners.etfs import ETFS
from screeners.config import config
from screeners.utils import retry
from screeners.scraper import login, scrape_screener, scrape_etf

with open('config-logging.yml', 'r') as config_logging:
  logging.config.dictConfig(yaml.safe_load(config_logging.read()))

logger = logging.getLogger(__name__)

def main(argv):
  username, password, cookies = argv[1:]
  retry_times = config['scraper']['retry_times']

  with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    if not cookies:
      login(page, username, password)
    else:
      decoded_cookies = base64.b64decode(cookies)
      page.context.add_cookies(json.loads(decoded_cookies))

    for etf in ETFS:
      for symbol in etf['US']:
        retry(retry_times)(lambda: scrape_etf(page, symbol))

    for screener in config['screeners']:

      screener_cache_name = screener['cache_name']
      screener_urls = screener['urls']

      for screener_url in screener_urls:
        retry(retry_times)(lambda: scrape_screener(page, screener_url, screener_cache_name))

if __name__ == '__main__':
  sys.exit(main(sys.argv))
