import json
import base64
import logging

from typing import List
from playwright.async_api import async_playwright

from screeners.config import config
from screeners.utils import unique_file_name
from screeners.scraper.login import login
from screeners.scraper.scrape import scrape

logger = logging.getLogger(__name__)

async def scrape_screener(username: str, password: str, cookies: str, target: str, urls: List[str]):

  async with async_playwright() as playwright:
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context()
    page = await context.new_page()

    if not cookies:
      await login(page, username, password)

      new_cookies = await page.context.cookies()
      with open(config['scraper']['cache_cookies'], "w") as f:
        f.write(json.dumps(new_cookies))
    else:
      decoded_cookies = base64.b64decode(cookies)
      await page.context.add_cookies(json.loads(decoded_cookies))

    for url in urls:
      logging.info('scraping screener %s', url)

      result_from_url = await scrape(page, url)
      result_from_url.to_csv(target + unique_file_name(extension='.csv'), index=False)
