import logging

import requests

from screeners.config import config

logger = logging.getLogger(__name__)


def log_to_telegram(text: str, bot_token: str, channel_id: str, message_id: str = ""):
    enabled = config["telegram"]["enabled"]

    if not enabled:
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    params = {"chat_id": channel_id, "text": text, "parse_mode": "HTML"}

    if message_id:
        params["reply_to_message_id"] = message_id

    response = requests.post(url, params=params)

    status_code = response.status_code
    if status_code != 200:
        logger.error(f"call to telegram failed with error code {status_code}")


def log_to_telegram_image(file, bot_token: str, channel_id: str, message_id: str = ""):
    enabled = config["telegram"]["enabled"]

    if not enabled:
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    files = {"photo": file}

    if message_id:
        files["reply_to_message_id"] = message_id

    response = requests.post(url, data={"chat_id": channel_id}, files=files)

    status_code = response.status_code
    if status_code != 200:
        logger.error(f"call to telegram failed with error code {status_code}")
