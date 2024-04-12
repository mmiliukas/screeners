#!/usr/bin/env python

import base64
import json
import sys

from playwright.sync_api import sync_playwright

from screeners.scraper import login


def main(argv):
    username, password = argv[1:]

    with sync_playwright() as playwright:

        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        login(page, username, password)

        cookies = json.dumps(page.context.cookies()).encode()
        print(base64.b64encode(cookies).decode("ascii"))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
