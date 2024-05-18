#!/usr/bin/env python

import sys

from screeners.telegram import log_to_telegram


def main(argv):
    """
    This script is and should be invoked
    whenever we have issues running scrapers
    and aggregating the data.
    """
    bot_token, channel_id = argv[1:]

    message = "<code>DAILY RUN FAILED!</code>"
    log_to_telegram(message, bot_token, channel_id)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
