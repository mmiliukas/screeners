import asyncio
import pandas

from io import StringIO
from datetime import datetime
from playwright.async_api import Page

from screeners.utils import a_number, a_string, a_percent, an_integer

async def scrape(page: Page, url: str):
  results = []

  await page.goto(url)
  await page.wait_for_selector("#scr-res-table")

  converters = {
    "Symbol": a_string,
    "Name": a_string,
    "Price (Intraday)": a_number,
    "Change": a_number,
    "% Change": a_percent,
    "Volume": an_integer,
    "Avg Vol (3 month)": an_integer,
    "Market Cap": an_integer
  }

  columns = [
    "Symbol",
    "Name",
    "Price (Intraday)",
    "Change",
    "% Change",
    "Volume",
    "Avg Vol (3 month)",
    "Market Cap"
  ]

  date = datetime.now().isoformat()

  while True:
    table = await page.wait_for_selector("#scr-res-table")
    html = '' if not table else await table.inner_html()

    data = pandas.read_html(StringIO(html), converters=converters)[0][columns] # type: ignore
    data.dropna(inplace=True)
    data["Date"] = date

    results.append(data)

    button = await page.wait_for_selector('#scr-res-table button span:has-text("Next")')
    if button:
      is_last = await button.is_disabled()
      if is_last:
        return pandas.concat(results)
      else:
        await button.click()
        await asyncio.sleep(2)
