import sys
import asyncio
import pandas
import time

from io import StringIO
from typing import List
from playwright.async_api import async_playwright, Page

async def login(page: Page, username: str, password: str):
    await page.goto("https://login.yahoo.com")
    await page.wait_for_selector("input#login-username")
    await page.type('input#login-username', username, delay=100)
    await page.click('input#login-signin')
    await page.wait_for_selector('input#login-passwd')
    await page.type('input#login-passwd', password, delay=120)
    await asyncio.sleep(2)
    await page.click('button#login-signin')
    await page.wait_for_selector('#Page.twelve-col')

async def scrape(page: Page, url: str):
    results = []

    await page.goto(url)
    await page.wait_for_selector("#scr-res-table")

    while True:
        table = await page.wait_for_selector("#scr-res-table")
        html = '' if not table else await table.inner_html()

        results.append(pandas.read_html(StringIO(html))[0])

        button = await page.wait_for_selector('#scr-res-table button span:has-text("Next")')
        if button:
            is_last = await button.is_disabled()
            if is_last:
                return results
            else:
                await button.click()
                await sleep(2)

async def main(username: str, password: str, urls: List[str]):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await login(page, username, password)

        for url in urls:
            result_from_url = await scrape(page, url)
            pandas.concat(result_from_url).to_csv('./runs/' + str(time.time()) + '.csv')

if __name__ == '__main__':
    username = sys.argv[1]
    password = sys.argv[2]
    urls = sys.argv[3:]

    asyncio.run(main(username, password, urls))
