"""Crash storage."""
from __future__ import annotations

from pathlib import Path
from typing import Dict


class CrashStorage:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path("data/results/crashes")
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, payload_id: str, details: str) -> Path:
        path = self.root / f"{payload_id}.log"
        path.write_text(details, encoding="utf-8")
        return path

    def list_crashes(self) -> Dict[str, str]:
        return {path.stem: path.read_text(encoding="utf-8") for path in self.root.glob("*.log")}


if __name__ == "__main__":
    storage = CrashStorage()
    storage.save("1", "boom")
    print(storage.list_crashes())
