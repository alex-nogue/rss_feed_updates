import json
from pathlib import Path
from typing import Dict, Any
import hashlib
from datetime import datetime, timezone

DEFAULT_STATE_FILE = Path("data/seen.json")


def load_state(path: Path = DEFAULT_STATE_FILE) -> Dict[str, Any]:
    if not path.exists():
        return {"seen": [], "last_run": None}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"seen": [], "last_run": None}


def save_state(state: Dict[str, Any], path: Path = DEFAULT_STATE_FILE):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def make_entry_id(entry) -> str:
    # Use id/link/title+published as deterministic unique key
    key = entry.get("id") or entry.get("link") or (entry.get("title", "") + entry.get("published", ""))
    if not isinstance(key, str):
        key = str(key)
    return hashlib.sha1(key.encode("utf-8")).hexdigest()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
