import logging

import requests

from screeners.config import config

logger = logging.getLogger(__name__)


def validate_telegram_response(response: requests.Response):
    status_code = response.status_code
    if status_code != 200:
        logger.error(f"call to telegram failed with error code {status_code}")
        # exit the process to let us know if reporting is failing
        raise Exception(f"call to telegram failed with error code {status_code}")


def minimize(multiline_string: str):
    """
    Telegram has a quota for message size/length.
    We need to minimize the payload to make sure all messages are sent through.
    """
    lines = multiline_string.splitlines()
    return "\n".join([line.rstrip() for line in lines])


def log_to_telegram(html: str, bot_token: str, channel_id: str):
    """
    Send a custom HTML snippet to telegram.
    You can use bold, italic, underlined, strikethrough,
    and spoiler text, as well as inline links and pre-formatted
    code in your bots' messages.

    https://core.telegram.org/bots/update56kabdkb12ibuisabdubodbasbdaosd#formatting-options
    """
    if not config["telegram"]["enabled"]:
        return logger.debug(minimize(html))

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    params = {
        "chat_id": channel_id,
        "text": minimize(html),
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    response = requests.post(url, params=params)

    validate_telegram_response(response)


def log_to_telegram_image(photo, bot_token: str, channel_id: str):
    """
    Uploads a photo to a given telegram channel.
    """
    if not config["telegram"]["enabled"]:
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    data = {"chat_id": channel_id}
    files = {"photo": photo}
    response = requests.post(url, data=data, files=files)

    validate_telegram_response(response)
