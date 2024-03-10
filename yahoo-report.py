import sys

from screeners.telegram import log_to_telegram

if __name__ == '__main__':
  bot_token, channel_id = sys.argv[1:]
  log_to_telegram('test', bot_token, channel_id)
