import logging
import re
from time import sleep

from playwright.sync_api import Page

logger = logging.getLogger(__name__)


def login(page: Page, username: str, password: str):
    login_url = "https://login.yahoo.com"

    logger.info(f'logging in into "{login_url}"...')

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
