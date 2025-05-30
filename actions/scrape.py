import logging
from time import sleep

from playwright.sync_api import sync_playwright

from screeners.config import config
from screeners.scraper import open_page, scrape_screener
from screeners.utils import abs_path, retry, unique_file_name

logger = logging.getLogger(__name__)


def scrape(name: str, cookies: str, cache_name: str, url: str) -> None:

    retry_times = config.scraper.retry_times

    with sync_playwright() as playwright:
        page = open_page(playwright, cookies)

        file_name = unique_file_name(extension=".csv")
        target = abs_path(cache_name, file_name)

        logger.info(f"scraping {name}")
        retry(retry_times)(lambda: scrape_screener(page, url, target))

        page.close()
        sleep(1)
