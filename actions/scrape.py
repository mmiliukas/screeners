import base64
import json

from playwright.sync_api import Request, Route, sync_playwright

from screeners.config import config
from screeners.scraper import scrape_screener
from screeners.utils import retry


def __block_heavy_requests(route: Route, request: Request) -> None:
    if request.resource_type in ["stylesheet", "image", "media", "font"]:
        route.abort()
    else:
        route.continue_()


def scrape(cookies: str) -> None:

    retry_times = config["scraper"]["retry_times"]

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        decoded_cookies = base64.b64decode(cookies)
        page.context.add_cookies(json.loads(decoded_cookies))

        page.route("**/*", __block_heavy_requests)

        for screener in config["screeners"]:

            # some screeners have no urls, cause we want to include
            # them inside a final dataframe
            screener_urls = screener["urls"] if "urls" in screener else []
            screener_cache_name = screener["cache_name"]

            for screener_url in screener_urls:
                retry(retry_times)(
                    lambda: scrape_screener(page, screener_url, screener_cache_name)
                )