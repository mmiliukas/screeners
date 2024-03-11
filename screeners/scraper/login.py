import logging

from time import sleep
from playwright.sync_api import Page

logger = logging.getLogger(__name__)

def login(page: Page, username: str, password: str):
  logger.info('logging in into yahoo.com...')

  page.goto("https://login.yahoo.com")
  page.wait_for_selector("input#login-username")
  page.type('input#login-username', username, delay=100)
  page.click('input#login-signin')
  page.wait_for_selector('input#login-passwd')
  page.type('input#login-passwd', password, delay=120)

  sleep(2)

  page.click('button#login-signin')
  page.wait_for_selector('#Page.twelve-col')
