import base64
import json

from playwright.sync_api import Page, Playwright, Request, Route


def __block_heavy_requests(route: Route, request: Request) -> None:
    if request.resource_type in ["stylesheet", "image", "media", "font"]:
        route.abort()
    else:
        route.continue_()


def open_page(playwright: Playwright, cookies: str) -> Page:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    decoded_cookies = base64.b64decode(cookies)
    page.context.add_cookies(json.loads(decoded_cookies))

    page.route("**/*", __block_heavy_requests)

    return page
