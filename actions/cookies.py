import base64
import json

from playwright.sync_api import sync_playwright


def cookies(username: str, password: str) -> str:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=False,
            channel="chrome",  # use real installed Chrome, not bundled Chromium
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://login.yahoo.com")

        input("Log in manually in the browser window, then press Enter to capture cookies...")

        result = json.dumps(page.context.cookies()).encode()
        return base64.b64encode(result).decode("ascii")
