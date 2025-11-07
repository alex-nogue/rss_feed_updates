import feedparser


def fetch_entries(url: str):
    """Return feed entries list for given RSS/Atom feed URL."""
    parsed = feedparser.parse(url)
    if parsed.bozo:
        # bozo flag indicates a parse error; still try to return entries
        # caller can decide how to handle
        pass
    return parsed.entries
