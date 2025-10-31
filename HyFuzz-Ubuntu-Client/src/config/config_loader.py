"""Utility helpers to read YAML configuration fragments."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml


def load_yaml(path: str | Path) -> Dict[str, Any]:
    file_path = Path(path)
    with file_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return data or {}


if __name__ == "__main__":
    sample = load_yaml(Path(__file__).with_name("default_config.yaml"))
    print(f"Sample keys: {list(sample.keys())}")
