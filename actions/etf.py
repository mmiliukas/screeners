import pandas as pd
from playwright.sync_api import ElementHandle, Page, sync_playwright
from tqdm import tqdm

from screeners.config import config
from screeners.etfs import ETFS
from screeners.scraper import open_page


def get_holding(el: ElementHandle) -> dict[str, str]:
    spans = el.query_selector_all("span")
    symbol, name, assets = [span.inner_text() for span in spans]
    return {"Name": name, "Symbol": symbol, "% Assets": assets}


def scrape(page: Page, symbol: str) -> None:
    url = f"https://finance.yahoo.com/quote/{symbol}/holdings"
    page.goto(url, wait_until="domcontentloaded")

    data_hook = '[data-testid="top-holdings"] div.container div.content'
    rows = page.query_selector_all(data_hook)

    df = pd.DataFrame(list(map(get_holding, rows)))
    df.to_csv(f"{config.etf.cache_name}{symbol}.csv", index=False)


def etf(cookies: str) -> None:

    etfs = [ticker for etf in ETFS for ticker in etf["US"]]

    with sync_playwright() as playwright:
        page = open_page(playwright, cookies)

        with tqdm(total=len(etfs)) as progress:
            for etf in etfs:
                progress.set_description(f"{etf:>10}", refresh=False)
                progress.update(1)

                scrape(page, etf)
