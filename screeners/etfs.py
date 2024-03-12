import glob

import pandas as pd

from screeners.config import config

ETFS = [
    {"EU": ["CRB", "SXPR"], "US": ["XLB"], "Sector": "Basic Materials"},
    {"EU": ["EXX1", "EUNB"], "US": ["XLF"], "Sector": "Financial Services"},
    {"EU": ["EXV6", "SX3E"], "US": ["XLP"], "Sector": "Consumer Defensive"},
    {"EU": ["EXH9", "UTIW"], "US": ["XLU"], "Sector": "Utilities"},
    {"EU": ["EXH1", "STN", "OILW"], "US": ["XLE"], "Sector": "Energy"},
    {
        "EU": ["EXV3", "LYX0GP", "DX2T", "STK"],
        "US": ["XLK", "VGT"],
        "Sector": "Technology",
    },
    {"EU": ["EXV5", "STP", "LYPH"], "US": ["XLY"], "Sector": "Consumer Cyclical"},
    {"EU": ["IPRP", "EURE", "XDER"], "US": ["XLRE", "VNQ"], "Sector": "Real Estate"},
    {"EU": ["EXV5", "HEALTH"], "US": ["XLV"], "Sector": "Healthcare"},
    {"EU": ["EXI3", "EXV4"], "US": ["XLC"], "Sector": "Communication Services"},
    {"EU": ["EXH1", "SI6E"], "US": ["XLI"], "Sector": "Industrials"},
]

SECTOR_ETF = {
    "Basic Materials": "XLB",
    "Financial Services": "XLF",
    "Consumer Defensive": "XLP",
    "Utilities": "XLU",
    "Energy": "XLE",
    "Technology": "XLK",
    "Consumer Cyclical": "XLY",
    "Real Estate": "XLRE",
    "Healthcare": "XLV",
    "Communication Services": "XLC",
    "Industrials": "XLI",
}


def get_etfs():
    all = set()
    for _ in ETFS:
        all.update(_["US"])
        # ignoring EU for now, we are focusing on US first
        # all.update(_["EU"])
    return list(all)


def get_etfs_and_holdings():
    etfs = get_etfs()

    cache_name = glob.glob(config["etf"]["cache_name"])
    df = pd.concat([pd.read_csv(csv) for csv in glob.glob(f"{cache_name}*.csv")])

    etfs.extend(df["Symbol"].unique())
    return etfs


def resolve_etf(sector):
    return SECTOR_ETF[sector] if sector in SECTOR_ETF else ""
