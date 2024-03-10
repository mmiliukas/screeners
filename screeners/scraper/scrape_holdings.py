import pandas

from io import StringIO
from playwright.async_api import Page

async def scrape_holdings(page: Page, symbol: str) -> pandas.DataFrame:
  await page.goto(f'https://finance.yahoo.com/quote/{symbol}/holdings')
  selector = await page.wait_for_selector('[data-test="top-holdings"]')
  html = '' if not selector else await selector.inner_html()
  data = pandas.read_html(StringIO(html))
  return data[0]
