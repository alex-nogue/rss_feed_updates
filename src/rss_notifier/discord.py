import requests
from typing import Any, Dict, Union


def build_message(entry: Any, feed: Dict) -> Dict[str, Any]:
    """Build a Discord webhook payload using an embed.

    The thumbnail is placed inside the embed's `thumbnail` object so Discord
    displays the image without showing its raw URL in the message body.
    """
    title = entry.get("title", "(no title)")
    link = entry.get("link", "")
    description = entry.get("description", "")
    thumbnail_url = entry.get("media_thumbnail", [])[0]["url"] if entry.get("media_thumbnail") else ""
    feed_name = feed.get("name", "Unknown Feed")

    # Build an embed. Set `title` and `url` so the title becomes a clickable link.
    embed: Dict[str, Any] = {
        "title": title,
        "description": description,
        "url": link if link else None,
        "image": {"url": thumbnail_url} if thumbnail_url else None
    }

    payload: Dict[str, Any] = {"embeds": [embed],
                               "content": f"Custom code: New feed article from **{feed_name}**"}
    
    # If want to pass the message to Discord as full text instead of embed payload
    # payload = f"**{title}**\n<{link}>\n{thumbnail_url}\n"

    return payload


def send_webhook(webhook_url: str, content: Union[str, Dict[str, Any]], timeout: int = 10):
    """Send content to a Discord webhook.
    """

    if isinstance(content, str):
        payload = {"content": content} # Case where we pass the Discord content as string
    else:
        payload = content              # Case where we pass the Discord content as embed payload

    resp = requests.post(webhook_url, json=payload, timeout=timeout)
    resp.raise_for_status()
    return resp
