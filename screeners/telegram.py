import requests

from screeners.config import config


def log_to_telegram(text: str, bot_token: str, channel_id: str):
    enabled = config["telegram"]["enabled"]

    if not enabled:
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    params = {"chat_id": channel_id, "text": text, "parse_mode": "HTML"}

    requests.post(url, params=params)
