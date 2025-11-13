import re
import sys
from pathlib import Path

# Ensure the package src directory is importable when running tests directly
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rss_notifier.filters import entry_text
from rss_notifier.rss_fetcher import fetch_entries
from rss_notifier.yaml_config import load_yaml_config, get_feeds_with_webhooks


def test_static_feed_filters():
    """Test filters against our static test feed."""
    # Load test config
    config = load_yaml_config(Path("tests/test_config.yaml"))
    feeds = get_feeds_with_webhooks(config)
    assert len(feeds) > 0, "No feeds found in test config"

    # Get first feed (our test feed)
    feed = feeds[0]
    entries = fetch_entries(feed['url'])
    assert len(entries) == 5, "Expected 5 entries in test feed"

    # Our filter pattern from test_config.yaml should match Frieren and Dandadan
    matches = []
    pattern = feed['pattern']  # Already compiled by get_feeds_with_webhooks

    for entry in entries:
        text = entry_text(entry)
        if pattern.search(text):
            matches.append(entry['title'])

    # We expect exactly these two titles to match
    expected_matches = [
        "Frieren: Beyond Journey's End Anime Announces Second Cour Details",
        "Dandadan Manga Gets TV Anime Adaptation for 2024",
        "Jujutsu Kaisen Season 2 Breaks Streaming Records"
    ]

    assert len(matches) == len(expected_matches), f"Expected {len(expected_matches)} matches but got {len(matches)}"
    for title in expected_matches:
        assert any(title in match for match in matches), f"Expected to match: {title}"