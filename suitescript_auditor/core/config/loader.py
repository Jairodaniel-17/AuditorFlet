"""Configuration loader."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from .defaults import defaults


def load_config(path: Path | None = None) -> Dict:
    if path is None:
        path = Path.home() / ".auditorrc.json"
    if not path.exists():
        return defaults.__dict__.copy()
    data = json.loads(path.read_text(encoding="utf-8"))
    merged = defaults.__dict__.copy()
    merged.update(data)
    return merged
