import logging
import os
from datetime import datetime
from io import StringIO
from time import sleep

import pandas
from playwright.sync_api import Page, TimeoutError

from screeners.utils import a_number, a_percent, a_string, an_integer, unique_file_name

logger = logging.getLogger(__name__)


def scrape_screener(page: Page, url: str, target: str):
    logger.info(f'scraping "{url}" to "{target}"...')

    results = []

    page.goto(url)
    page.wait_for_selector("#fin-scr-res-table")

    try:
        page.query_selector("#fin-scr-res-table #scr-res-table")
    except TimeoutError:
        # sometimes screener might return no results
        logger.info(f'screener "{url}" returned empty results, skipping...')
        return

    converters = {
        "Symbol": a_string,
        "Name": a_string,
        "Price (Intraday)": a_number,
        "Change": a_number,
        "% Change": a_percent,
        "Volume": an_integer,
        "Avg Vol (3 month)": an_integer,
        "Market Cap": an_integer,
    }

    columns = [
        "Symbol",
        "Name",
        "Price (Intraday)",
        "Change",
        "% Change",
        "Volume",
        "Avg Vol (3 month)",
        "Market Cap",
    ]

    date = datetime.now().isoformat()

    while True:
        table = page.wait_for_selector("#scr-res-table")
        html = "" if not table else table.inner_html()

        data = pandas.read_html(StringIO(html), converters=converters)[0][columns]  # type: ignore
        data.dropna(inplace=True)
        data["Date"] = date

        results.append(data)

        button = page.wait_for_selector('#scr-res-table button span:has-text("Next")')
        if button:
            is_last = button.is_disabled()
            if is_last:
                if not os.path.exists(target):
                    os.makedirs(target)

                pandas.concat(results).to_csv(
                    target + unique_file_name(extension=".csv"), index=False
                )

                return
            else:
                button.click()
                sleep(2)
