import logging
from datetime import datetime
from io import StringIO
from time import sleep

import pandas as pd
from playwright.sync_api import Page, TimeoutError

from screeners.config import config
from screeners.utils import a_number, a_percent, a_string, an_integer

logger = logging.getLogger(__name__)


def a_symbol(value: str) -> str:
    parts = a_string(value).split(" ")
    return parts[1] if len(parts) > 1 else parts[0]


converters: dict = {
    "Symbol": a_symbol,
    "Name": a_string,
    "Price (Intraday)": a_number,
    "Change": a_number,
    "Change %": a_percent,
    "Volume": an_integer,
    "Avg Vol (3M)": an_integer,
    "Market Cap": an_integer,
}

columns = [
    "Symbol",
    "Name",
    "Price (Intraday)",
    "Change",
    "Change %",
    "Volume",
    "Avg Vol (3M)",
    "Market Cap",
]

rename_columns = {
    "Change %": "% Change",
    "Avg Vol (3M)": "Avg Vol (3 month)",
}


selector_screener_name = ".screenerName"
selector_table = ".screener-table .table-container"


def scrape_screener(page: Page, url: str, target: str) -> None:
    results = []
    offset = 0
    date = datetime.now().isoformat()

    page.set_viewport_size({"width": 2040, "height": 1080})

    while True:
        url_to_scape = url if offset == 0 else f"{url}&start={offset}"
        logger.info(f"scraping {offset:>4} from {url_to_scape} to {target}...")

        df = scrape_screener_single(page, url_to_scape, date)

        if df.empty:
            logger.info("empty result, stopping...")
            break

        results.append(df)
        offset += 100

        sleep(config.scraper.sleep_after_click)

    pd.concat(results).to_csv(target, index=False)


def scrape_screener_single(page: Page, url: str, date: str) -> pd.DataFrame:
    page.goto(url)

    try:
        page.wait_for_selector(selector_screener_name)
    except TimeoutError:
        logger.error(f"screener {url} not found, might be session has expired")
        raise Exception(f"screener {url} not found, might be session has expired")

    try:
        page.wait_for_selector(
            f"{selector_table} > table thead tr", state="visible", strict=True
        )
        page.wait_for_timeout(1_000)
    except TimeoutError:
        logger.info(f"screener {url} returned empty results, skipping...")
        return pd.DataFrame()

    table = page.wait_for_selector(selector_table)
    html = "" if not table else table.inner_html()

    data = pd.read_html(StringIO(html), converters=converters)[0]
    if data.empty:
        return pd.DataFrame()

    data = data[columns].dropna()
    data["Date"] = date
    data = data.rename(columns=rename_columns)

    return data
