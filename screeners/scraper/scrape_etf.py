import pandas as pd
from playwright.sync_api import ElementHandle, Page

from screeners.config import config
from screeners.utils import abs_path


def __get_holding(el: ElementHandle) -> dict[str, str]:
    spans = el.query_selector_all("span")
    symbol, name, assets = [span.inner_text() for span in spans]
    return {"Name": name, "Symbol": symbol, "% Assets": assets}


def scrape_etf(page: Page, symbol: str) -> None:
    url = f"https://finance.yahoo.com/quote/{symbol}/holdings"
    page.goto(url, wait_until="domcontentloaded")

    data_hook = '[data-testid="top-holdings"] div.container div.content'
    rows = page.query_selector_all(data_hook)

    target = abs_path(config["etf"]["cache_name"])

    df = pd.DataFrame(list(map(__get_holding, rows)))
    df.to_csv(f"{target}{symbol}.csv", index=False)
