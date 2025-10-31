"""Scan targets from local data files."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List


class TargetScanner:
    def __init__(self, target_file: Path | None = None) -> None:
        self.target_file = target_file or Path("data/targets/target_profiles.json")

    def scan(self) -> List[dict[str, object]]:
        if not self.target_file.exists():
            return []
        data = json.loads(self.target_file.read_text(encoding="utf-8"))
        return data.get("targets", [])  # type: ignore[return-value]


if __name__ == "__main__":
    print(TargetScanner().scan())
