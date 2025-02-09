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


selector_table = ".screener-table .table-container"
selector_id = f"{selector_table} table tbody tr:first-child td:first-child"
selector_button = "button[data-testid='next-page-button']"


def scrape_screener(page: Page, url: str, target: str) -> None:
    logger.info(f"scraping {url} to {target}...")

    page.goto(url)

    try:
        page.wait_for_selector(selector_table)
    except TimeoutError:
        logger.info(f"screener {url} returned empty results, skipping...")
        return

    results = []
    page_no = 1
    date = datetime.now().isoformat()

    while True:
        table = page.wait_for_selector(selector_table)
        html = "" if not table else table.inner_html()

        data = pd.read_html(StringIO(html), converters=converters)[0]
        data = data[columns].dropna()
        data["Date"] = date
        data = data.rename(columns=rename_columns)

        results.append(data)

        try:
            button = page.wait_for_selector(selector_button, timeout=5000)
        except Exception:
            button = None

        is_last = not button or button.is_disabled()
        if is_last:
            pd.concat(results).to_csv(target, index=False)
            return

        page_no += 1
        logger.info(f"going to next page {page_no:>3}...")

        id = page.query_selector(selector_id)
        assert id is not None, "id not found"

        initial_content = id.inner_text()
        logger.info(initial_content)
        button.click()  # type: ignore

        page.wait_for_function(
            """([selector, initialContent]) => {
                const element = document.querySelector(selector);
                return element && element.innerText !== initialContent;
            }""",
            arg=[selector_id, initial_content],
        )

        sleep(config.scraper.sleep_after_click)
