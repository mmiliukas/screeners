import re
from time import sleep

from playwright.sync_api import Page


def login(page: Page, username: str, password: str) -> None:
    login_url = "https://login.yahoo.com"

    page.goto(login_url)
    page.wait_for_selector("input#login-username")
    page.type("input#login-username", username, delay=100)
    page.click("input#login-signin")
    page.wait_for_selector("input#login-passwd")
    page.type("input#login-passwd", password, delay=120)

    sleep(2)

    page.click("button#login-signin")

    url_to_wait = re.compile(".*www.yahoo.com.*", re.IGNORECASE)
    page.wait_for_url(url_to_wait, wait_until="domcontentloaded")
