"""Main runner: fetch RSS, filter new items, send webhook, persist state."""
from pathlib import Path
import logging
from typing import Dict, Any, List, Tuple
from .rss_fetcher import fetch_entries
from .filters import entry_text
from .state import load_state, save_state, make_entry_id, now_iso
from .yaml_config import load_yaml_config, get_feeds_with_webhooks
import sys

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)


def process_feed(feed: Dict[str, Any], seen: set) -> Tuple[List[Tuple[str, Any]], List[Tuple[str, Any]]]:
    """Process a single feed, return (new_entries, matched_entries)."""
    entries = fetch_entries(feed['url'])
    if not entries:
        return [], []

    new_added = []
    matched = []

    for entry in entries:
        eid = make_entry_id(entry)
        if eid in seen:
            continue
        new_added.append((eid, entry))

        # Check if entry matches feed's regex pattern
        if feed['pattern'].search(entry_text(entry)):
            matched.append((eid, entry))

    return new_added, matched


def run_once(config_path: Path = Path("config.yaml")):
    """Run one iteration: fetch all enabled feeds, filter, notify, update state."""
    # Load config and state
    config = load_yaml_config(config_path)
    state = load_state()
    seen = set(state.get("seen", []))
    
    # Process each feed (webhooks and patterns are already resolved)
    feeds = get_feeds_with_webhooks(config)
    if not feeds:
        raise ValueError("No feeds found in config")

    all_new = []
    all_matched = []
    
    for feed in feeds:
        try:
            new_added, matched = process_feed(feed, seen)
            all_new.extend(new_added)
            all_matched.extend([(eid, entry, feed) for eid, entry in matched])
        except Exception as e:
            logging.error(f"Failed to process feed {feed['name']}: {e}")
            raise

    # Send notifications for matches
    if all_matched:
        from .discord import send_webhook, build_message
        logging.info(f"Found {len(all_matched)} matching entries across all feeds")
        
        for eid, entry, feed in all_matched:
            content = build_message(entry)
            webhook_url = feed['webhook_url']
            send_webhook(webhook_url, content)
            logging.info(f"Sent webhook for: {entry.get('title')} to {feed['name']} webhook")
    else:
        logging.info(f"No new matching entries (checked {len(all_new)} new entries)")

    # Update state with all new entries
    for eid, _ in all_new:
        seen.add(eid)

    state["seen"] = list(seen)
    state["last_run"] = now_iso()
    save_state(state)


def main():
    """Main entry point with argument parsing."""
    import argparse
    
    parser = argparse.ArgumentParser(description='RSS feed monitor with Discord notifications')
    parser.add_argument('--config', type=Path, default='config.yaml',
                      help='Path to YAML config file (default: config.yaml)')
    args = parser.parse_args()

    try:
        run_once(config_path=args.config)
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
