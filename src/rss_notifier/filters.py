def entry_text(entry) -> str:
    """Extract searchable text from an RSS entry."""
    parts = []
    for key in ("title", "summary", "description"):
        val = entry.get(key)
        if val:
            parts.append(val)
    return "\n".join(parts)
