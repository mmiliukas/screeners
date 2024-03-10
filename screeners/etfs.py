SECTOR_ETF = {
  'Basic Materials': 'XLB',
  'Financial Services': 'XLF',
  'Consumer Defensive': 'XLP',
  'Utilities': 'XLU',
  'Energy': 'XLE',
  'Technology': 'XLK',
  'Consumer Cyclical': 'XLY',
  'Real Estate': 'XLRE',
  'Healthcare': 'XLV',
  'Communication Services': 'XLC',
  'Industrials': 'XLI'
}

def resolve_etf(sector):
  return SECTOR_ETF[sector] if sector in SECTOR_ETF else ''
