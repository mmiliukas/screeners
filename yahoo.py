import sys
import time
import asyncio
import pandas

from datetime import datetime
from io import StringIO
from typing import List
from playwright.async_api import async_playwright, Page

def a_string(x: str):
   return x

def a_percent(x: str):
  try:
    return round(float(x.replace('%', '')), 4)
  except Exception:
    return round(0, 4)

def a_number(x: str):
  multipliers = {
    'k': 10**3,
    'K': 10**3,
    'm': 10**6,
    'M': 10**6,
    'b': 10**9,
    'B': 10**9
  }

  try:
    if x[-1] in multipliers:
      return round(float(x[:-1]) * multipliers[x[-1]], 4)
    else:
      return float(x)
  except Exception:
    return round(0, 4)

def an_integer(x: str):
  try:
    return int(a_number(x))
  except Exception:
    return 0

def a_csv_file_name():
    return './runs/' + time.strftime('%Y_%m_%d_%H_%M_%S') + '.csv'

async def login(page: Page, username: str, password: str):
    await page.goto("https://login.yahoo.com")
    await page.wait_for_selector("input#login-username")
    await page.type('input#login-username', username, delay=100)
    await page.click('input#login-signin')
    await asyncio.sleep(2)
    await page.screenshot(path="./runs/abc.jpg")
    await page.wait_for_selector('input#login-passwd')
    await page.type('input#login-passwd', password, delay=120)
    await asyncio.sleep(2)
    await page.click('button#login-signin')
    await page.wait_for_selector('#Page.twelve-col')

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

async def main(username: str, password: str, urls: List[str]):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await login(page, username, password)

        for url in urls:
            result_from_url = await scrape(page, url)
            result_from_url.to_csv(a_csv_file_name(), index=False)

if __name__ == '__main__':
    username = sys.argv[1]
    password = sys.argv[2]
    urls = sys.argv[3:]

    asyncio.run(main(username, password, urls))
