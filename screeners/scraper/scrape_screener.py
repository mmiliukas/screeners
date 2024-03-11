import json
import base64
import logging

from typing import List
from playwright.sync_api import sync_playwright

from screeners.config import config
from screeners.utils import unique_file_name
from screeners.scraper.login import login
from screeners.scraper.scrape import scrape

logger = logging.getLogger(__name__)

def scrape_screener(username: str, password: str, cookies: str, target: str, urls: List[str]):

  with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    if not cookies:
      login(page, username, password)

      new_cookies = page.context.cookies()
      with open(config['scraper']['cache_cookies'], "w") as f:
        f.write(json.dumps(new_cookies))
    else:
      decoded_cookies = base64.b64decode(cookies)
      page.context.add_cookies(json.loads(decoded_cookies))

    for url in urls:
      logging.info('scraping screener %s', url)

      result_from_url = scrape(page, url)
      result_from_url.to_csv(target + unique_file_name(extension='.csv'), index=False)
