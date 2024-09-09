from io import StringIO

import pandas as pd
from playwright.sync_api import Page

from screeners.config import config
from screeners.utils import abs_path


def scrape_etf(page: Page, symbol: str) -> None:
    url = f"https://finance.yahoo.com/quote/{symbol}/holdings"
    page.goto(url, wait_until="domcontentloaded")

    data_hook = '[data-test="top-holdings"]'

    table = page.wait_for_selector(data_hook)
    html = "" if not table else table.inner_html()

    df = pd.read_html(StringIO(html))[0]

    target = abs_path(config["etf"]["cache_name"])
    df.to_csv(f"{target}{symbol}.csv", index=False)
