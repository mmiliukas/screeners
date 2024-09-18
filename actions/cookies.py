import base64
import json

from playwright.sync_api import sync_playwright

from screeners.scraper import login


def cookies(username: str, password: str) -> str:
    with sync_playwright() as playwright:

        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        login(page, username, password)

        cookies = json.dumps(page.context.cookies()).encode()
        return base64.b64encode(cookies).decode("ascii")
