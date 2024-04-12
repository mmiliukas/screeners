import base64
import json
import logging
import logging.config
import sys

import yaml
from playwright.sync_api import sync_playwright

from screeners.config import config
from screeners.etfs import get_etfs
from screeners.scraper import scrape_etf, scrape_screener
from screeners.utils import retry

with open("config-logging.yml", "r") as config_logging:
    logging.config.dictConfig(yaml.safe_load(config_logging.read()))

logger = logging.getLogger(__name__)


def main(argv):

    cookies = argv[1]
    retry_times = config["scraper"]["retry_times"]

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        decoded_cookies = base64.b64decode(cookies)
        page.context.add_cookies(json.loads(decoded_cookies))

        for etf in get_etfs():
            retry(retry_times)(lambda: scrape_etf(page, etf))

        for screener in config["screeners"]:

            screener_cache_name = screener["cache_name"]
            screener_urls = screener["urls"] if "url" in screener else []

            for screener_url in screener_urls:
                retry(retry_times)(
                    lambda: scrape_screener(page, screener_url, screener_cache_name)
                )


if __name__ == "__main__":
    sys.exit(main(sys.argv))
