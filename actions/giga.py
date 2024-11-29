from playwright.sync_api import sync_playwright

from screeners.config import config
from screeners.scraper import open_page, scrape_screener
from screeners.utils import abs_path, retry


def giga(cookies: str, index: int) -> None:

    retry_times = config["scraper"]["retry_times"]
    giga = config["giga"][index]
    to_file_name = abs_path(giga["target"])

    with sync_playwright() as playwright:
        page = open_page(playwright, cookies)
        retry(retry_times)(lambda: scrape_screener(page, giga["url"], to_file_name))
