from playwright.sync_api import sync_playwright
from tqdm import tqdm

from screeners.config import config
from screeners.etfs import ETFS
from screeners.scraper import open_page, scrape_etf
from screeners.utils import retry


def etf(cookies: str) -> None:

    retry_times = config.scraper.retry_times
    etfs = [ticker for etf in ETFS for ticker in etf["US"]]

    with sync_playwright() as playwright:
        page = open_page(playwright, cookies)

        with tqdm(total=len(etfs)) as progress:
            for etf in etfs:
                progress.set_description(f"{etf:>10}", refresh=False)
                progress.update(1)

                retry(retry_times)(lambda: scrape_etf(page, etf))
