#!/usr/bin/env python

import sys

from screeners.telegram import log_to_telegram


def main(argv):
    bot_token, channel_id = argv[1:]

    message = "<code>DAILY RUN FAILED!</code>"
    log_to_telegram(message, bot_token, channel_id)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
