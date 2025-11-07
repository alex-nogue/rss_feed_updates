import requests
from typing import Any


def build_message(entry: Any) -> str:
    title = entry.get("title", "(no title)")
    link = entry.get("link", "")
    published = entry.get("published", "")
    summary = entry.get("summary", "")
    # msg = f"**{title}**\n{published}\n{link}\n\n{summary}"
    msg = f"**{title}**\n{link}"
    return msg


def send_webhook(webhook_url: str, content: str, timeout: int = 10):
    if not webhook_url:
        raise ValueError("No webhook URL provided")
    payload = {"content": content}
    resp = requests.post(webhook_url, json=payload, timeout=timeout)
    resp.raise_for_status()
    return resp
