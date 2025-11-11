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
        regex_name = feed['regex']
        regex_pattern = config['filters'][regex_name]
        concatenated_series = "|".join(config['series'].values())
        regex_pattern = regex_pattern.replace('placeholder', concatenated_series)
        feed_copy['pattern'] = re.compile(regex_pattern)
        result.append(feed_copy)

    return result


def load_yaml_config(path: Path = DEFAULT_CONFIG_PATH) -> Dict[str, Any]:
    """Load and validate YAML configuration file."""

    with open(path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    return config