"""
platform/telegram/helpers.py
Low-level Telegram Bot API calls via requests.
Intentionally thin — no python-telegram-bot abstraction here so we stay
in control of the webhook flow.
"""
import requests

TELEGRAM_API = "https://api.telegram.org/bot{token}/{method}"


def _call(token: str, method: str, **kwargs) -> dict:
    url = TELEGRAM_API.format(token=token, method=method)
    r = requests.post(url, json=kwargs, timeout=10)
    r.raise_for_status()
    return r.json()


def send_message(token: str, chat_id: int, text: str,
                 parse_mode: str = "Markdown") -> dict:
    return _call(token, "sendMessage", chat_id=chat_id,
                 text=text, parse_mode=parse_mode)


def send_chat_action(token: str, chat_id: int,
                     action: str = "typing") -> dict:
    return _call(token, "sendChatAction", chat_id=chat_id, action=action)


def set_webhook(token: str, webhook_url: str) -> dict:
    """Register webhook URL with Telegram."""
    result = _call(token, "setWebhook", url=webhook_url)
    print(f"setWebhook → {result}")
    return result


def delete_webhook(token: str) -> dict:
    return _call(token, "deleteWebhook")


def get_webhook_info(token: str) -> dict:
    url = TELEGRAM_API.format(token=token, method="getWebhookInfo")
    return requests.get(url, timeout=10).json()
