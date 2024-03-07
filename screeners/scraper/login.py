import asyncio

from playwright.async_api import Page

async def login(page: Page, username: str, password: str):
  await page.goto("https://login.yahoo.com")
  await page.wait_for_selector("input#login-username")
  await page.type('input#login-username', username, delay=100)
  await page.click('input#login-signin')
  await page.wait_for_selector('input#login-passwd')
  await page.type('input#login-passwd', password, delay=120)
  await asyncio.sleep(2)
  await page.click('button#login-signin')
  await page.wait_for_selector('#Page.twelve-col')
