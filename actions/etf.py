from playwright.sync_api import sync_playwright
from tqdm import tqdm

from screeners.config import config
from screeners.etfs import get_etfs
from screeners.scraper import open_page, scrape_etf
from screeners.utils import retry


def etf(cookies: str) -> None:

    retry_times = config.scraper.retry_times
    etfs = get_etfs()

    with sync_playwright() as playwright:
        page = open_page(playwright, cookies)

        with tqdm(total=len(etfs)) as progress:
            for etf in etfs:
                retry(retry_times)(lambda: scrape_etf(page, etf))

                progress.set_description(f"{etf:>10}", refresh=False)
                progress.update(1)
