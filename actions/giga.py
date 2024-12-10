import logging

from playwright.sync_api import sync_playwright

from screeners.config import config
from screeners.scraper import open_page, scrape_screener

logger = logging.getLogger(__name__)


def giga(cookies: str, index: int) -> None:
    giga = config.giga[index]
    logger.info(f"scraping {giga.name}")

    with sync_playwright() as playwright:
        page = open_page(playwright, cookies)
        scrape_screener(page, giga.url, giga.target)
