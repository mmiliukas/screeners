import json
import base64
import pandas
import logging

from io import StringIO
from playwright.async_api import Page, async_playwright

from screeners.scraper.login import login
from screeners.etfs import ETFS

logger = logging.getLogger(__name__)

async def scrape_holdings(page: Page, symbol: str) -> pandas.DataFrame:
  await page.goto(f'https://finance.yahoo.com/quote/{symbol}/holdings')
  selector = await page.wait_for_selector('[data-test="top-holdings"]')
  html = '' if not selector else await selector.inner_html()
  data = pandas.read_html(StringIO(html))
  return data[0]

async def scrape_etfs(username: str, password: str, cookies: str):

  async with async_playwright() as playwright:
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context()
    page = await context.new_page()

    if not cookies:
      await login(page, username, password)
    else:
      decoded_cookies = base64.b64decode(cookies)
      await page.context.add_cookies(json.loads(decoded_cookies))

    for etf in ETFS:
      for symbol in etf['US']:
        logger.info('scraping holdings for %s', symbol)
        df = await scrape_holdings(page, symbol)
        df.to_csv(f'./etfs/{symbol}.csv', index=False)
