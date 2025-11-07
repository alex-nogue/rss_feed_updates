"""Configuration loading and validation."""
from pathlib import Path
import yaml
from typing import Dict, Any, List
import os
import re

DEFAULT_CONFIG_PATH = Path("config.yaml")
ENV_VAR_PATTERN = re.compile(r'\${([^}]+)}')


def substitute_env_vars(value: str) -> str:
    """Replace ${ENV_VAR} with environment variable values."""
    def replace_env_var(match):
        env_var = match.group(1)
        if env_var not in os.environ:
            raise ValueError(f"Required environment variable not set: {env_var}")
        return os.environ[env_var]
    
    return ENV_VAR_PATTERN.sub(replace_env_var, value)


def get_feeds_with_webhooks(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return feeds with resolved webhook URLs and compiled regex patterns."""
    result = []
    
    for feed in config['feeds']:
        # Deep copy the feed to avoid modifying the config
        feed_copy = feed.copy()
        
        # Resolve webhook URL
        webhook_name = feed['webhook']
        webhook_url = config['webhooks'][webhook_name]
        feed_copy['webhook_url'] = substitute_env_vars(webhook_url)

        # Pre-compile the regex pattern
        feed_copy['pattern'] = re.compile(feed['regex'])
        result.append(feed_copy)

    return result


def load_yaml_config(path: Path = DEFAULT_CONFIG_PATH) -> Dict[str, Any]:
    """Load and validate YAML configuration file."""
    if not path.exists():
        raise ValueError(f"Config file not found: {path}")

    with open(path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # Validate required sections
    if not isinstance(config, dict):
        raise ValueError("Invalid config format: must be a YAML document")

    if 'feeds' not in config or not isinstance(config['feeds'], list):
        raise ValueError("Config must have a 'feeds' list")
    if 'webhooks' not in config or not isinstance(config['webhooks'], dict):
        raise ValueError("Config must have a 'webhooks' dictionary")

    # Validate webhooks
    for name, url in config['webhooks'].items():
        try:
            resolved_url = substitute_env_vars(url)
            if not resolved_url.startswith(('http://', 'https://')):
                raise ValueError(f"Invalid webhook URL format for {name}")
        except ValueError as e:
            raise ValueError(f"Error in webhook {name}: {e}")

    # Validate feeds
    valid_webhook_names = set(config['webhooks'].keys())
    for i, feed in enumerate(config['feeds']):
        if not isinstance(feed, dict):
            raise ValueError(f"Feed {i} must be a dictionary")
        
        # Check required fields
        required_fields = {'name', 'url', 'webhook', 'regex'}
        missing = required_fields - set(feed.keys())
        if missing:
            raise ValueError(f"Feed {feed.get('name', i)} missing required fields: {missing}")

        # Validate webhook reference
        if feed['webhook'] not in valid_webhook_names:
            raise ValueError(f"Feed {feed['name']} references undefined webhook: {feed['webhook']}")

        # Validate regex
        try:
            re.compile(feed['regex'])
        except re.error:
            raise ValueError(f"Feed {feed['name']} has invalid regex pattern: {feed['regex']}")

    return config