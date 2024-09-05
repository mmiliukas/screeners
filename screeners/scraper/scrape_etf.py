import logging

import pandas as pd
from playwright.sync_api import ElementHandle, Page

from screeners.config import config

logger = logging.getLogger(__name__)


def __get_holding(el: ElementHandle) -> dict[str, str]:
    symbol, name, assets = el.inner_text().strip().split("\n")
    return {"Name": name, "Symbol": symbol, "% Assets": assets}


def scrape_etf(page: Page, symbol: str) -> None:
    page.goto(f"https://finance.yahoo.com/quote/{symbol}/holdings")

    data_hook = '[data-testid="top-holdings"] div.container div.content'
    page.wait_for_selector(data_hook)

    rows = page.query_selector_all(data_hook)

    etf_cache_name = config["etf"]["cache_name"]

    df = pd.DataFrame(list(map(__get_holding, rows)))
    df.to_csv(f"{etf_cache_name}{symbol}.csv", index=False)
