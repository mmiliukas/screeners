import asyncio
import logging

from playwright.async_api import Page

logger = logging.getLogger(__name__)

async def login(page: Page, username: str, password: str):
  logger.info('logging in into yahoo.com...')

  await page.goto("https://login.yahoo.com")
  await page.wait_for_selector("input#login-username")
  await page.type('input#login-username', username, delay=100)
  await page.click('input#login-signin')
  await page.wait_for_selector('input#login-passwd')
  await page.type('input#login-passwd', password, delay=120)
  await asyncio.sleep(2)
  await page.click('button#login-signin')
  await page.wait_for_selector('#Page.twelve-col')
