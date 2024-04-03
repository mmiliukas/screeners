import io

import requests

from screeners.config import config


def log_to_telegram(text: str, bot_token: str, channel_id: str):
    enabled = config["telegram"]["enabled"]

    if not enabled:
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    params = {"chat_id": channel_id, "text": text, "parse_mode": "HTML"}

    requests.post(url, params=params)


def log_to_telegram_image(file, bot_token: str, channel_id: str):
    enabled = config["telegram"]["enabled"]

    if not enabled:
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    files = {"photo": file}

    response = requests.post(url, data={"chat_id": channel_id}, files=files)

    if response.status_code == 200:
        print("Image uploaded successfully!")
    else:
        print("Failed to upload image:", response.text)
