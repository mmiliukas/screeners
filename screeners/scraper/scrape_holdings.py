import json
import base64
import pandas
import logging

from io import StringIO
from playwright.sync_api import Page, sync_playwright

from screeners.scraper.login import login
from screeners.etfs import ETFS

logger = logging.getLogger(__name__)

def scrape_holdings(page: Page, symbol: str) -> pandas.DataFrame:
  page.goto(f'https://finance.yahoo.com/quote/{symbol}/holdings')
  selector = page.wait_for_selector('[data-test="top-holdings"]')
  html = '' if not selector else selector.inner_html()
  data = pandas.read_html(StringIO(html))
  return data[0]

def scrape_etfs(username: str, password: str, cookies: str):

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
        logger.info('scraping holdings for %s', symbol)
        df = scrape_holdings(page, symbol)
        df.to_csv(f'./etfs/{symbol}.csv', index=False)
