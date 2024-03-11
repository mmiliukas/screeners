import sys
import yaml
import logging
import logging.config

from screeners.config import config
from screeners.utils import retry
from screeners.scraper import scrape_screener, scrape_etfs

with open('config-logging.yml', 'r') as config_logging:
  logging.config.dictConfig(yaml.safe_load(config_logging.read()))

logger = logging.getLogger(__name__)

def main(argv):
  username, password, cookies = argv[1:]
  retry_times = config['scraper']['retry_times']

  retry(retry_times)(lambda: scrape_etfs(username, password, cookies))

  for screener in config['screeners']:

    screener_cache_name = screener['cache_name']
    screener_urls = screener['urls']

    retry(retry_times)(lambda: scrape_screener(username, password, cookies, screener_cache_name, screener_urls))

if __name__ == '__main__':
  sys.exit(main(sys.argv))
