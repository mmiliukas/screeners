import logging
from io import StringIO

import pandas
from playwright.sync_api import Page

from screeners.config import config

logger = logging.getLogger(__name__)


def scrape_etf(page: Page, symbol: str):
    logger.info(f'scraping holdings for ETF "{symbol}"...')

    page.goto(f"https://finance.yahoo.com/quote/{symbol}/holdings")
    selector = page.wait_for_selector('[data-test="top-holdings"]')

    html = "" if not selector else selector.inner_html()

    data = pandas.read_html(StringIO(html))
    etf_cache_name = config["etf"]["cache_name"]

    data[0].to_csv(f"{etf_cache_name}{symbol}.csv", index=False)
