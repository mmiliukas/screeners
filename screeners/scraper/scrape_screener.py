import logging
import os
from datetime import datetime
from io import StringIO
from time import sleep

import pandas as pd
from playwright.sync_api import Page, TimeoutError

from screeners.config import config
from screeners.utils import a_number, a_percent, a_string, an_integer

logger = logging.getLogger(__name__)


def scrape_screener(page: Page, url: str, target: str) -> None:
    logger.info(f"scraping {url} to {target}...")

    results = []

    page.goto(url)
    page.wait_for_selector("#fin-scr-res-table")

    try:
        page.wait_for_selector("#fin-scr-res-table #scr-res-table")
    except TimeoutError:
        logger.info(f"screener {url} returned empty results, skipping...")
        return

    converters: dict = {
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
    page_no = 1

    while True:
        table = page.wait_for_selector("#scr-res-table")
        html = "" if not table else table.inner_html()

        data = pd.read_html(StringIO(html), converters=converters)[0][columns]
        data.dropna(inplace=True)
        data["Date"] = date

        results.append(data)

        if len(data) == 100:
            sleep(config["scraper"]["sleep_after_click"])

            page.goto(f"{url}&offset={page_no * 100}")
            page_no += 1
            logger.info(f"going to next page {page_no}...")
        else:
            dir = os.path.dirname(target)
            os.makedirs(dir, exist_ok=True)
            pd.concat(results).to_csv(target, index=False)
            return
