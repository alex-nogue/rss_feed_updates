from pathlib import Path
import os
import re
import logging

DEFAULT_KEYWORDS_FILE = Path("keywords.txt")


def load_keywords(path: Path = DEFAULT_KEYWORDS_FILE):
    """Load keywords and regex patterns from a plain text file.

    Format:
    - blank lines and lines starting with # are ignored
    - lines starting with 'r:' are treated as regex patterns (case-insensitive)
    - other lines are treated as simple keywords (case-insensitive, substring match)
    Returns (keywords_list, regex_list)
    """
    kws = []
    regexes = []
    if not Path(path).exists():
        return kws, regexes

    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("r:"):
            pattern = line[2:].strip()
            if not pattern:
                continue
            try:
                regexes.append(re.compile(pattern, re.I))
            except re.error:
                # ignore invalid regex patterns, but continue
                continue
        else:
            kws.append(line.lower())

    return kws, regexes


def get_webhook_url():
    # Placeholder — prefer using an environment variable or GitHub secret
    return os.getenv("DISCORD_WEBHOOK_URL", "")


def setup_logging():
    """Configure logging with appropriate level and format."""
    level = logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )