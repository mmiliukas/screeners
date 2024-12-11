from playwright.sync_api import sync_playwright

from screeners.config import config
from screeners.scraper import open_page, scrape_screener


def giga(cookies: str, index: int) -> None:
    giga = config.giga[index]

    with sync_playwright() as playwright:
        page = open_page(playwright, cookies)
        scrape_screener(page, giga.url, giga.target)
