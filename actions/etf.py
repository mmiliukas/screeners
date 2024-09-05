import base64
import json

from playwright.sync_api import sync_playwright
from tqdm import tqdm

from screeners.config import config
from screeners.etfs import get_etfs
from screeners.scraper import scrape_etf
from screeners.utils import retry


def etf(cookies: str) -> None:

    retry_times = config["scraper"]["retry_times"]

    etfs = get_etfs()
    with tqdm(total=len(etfs)) as progress:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            decoded_cookies = base64.b64decode(cookies)
            page.context.add_cookies(json.loads(decoded_cookies))

            for etf in get_etfs():
                retry(retry_times)(lambda: scrape_etf(page, etf))

                progress.set_description(f"{etf:<10}", refresh=False)
                progress.update(1)
