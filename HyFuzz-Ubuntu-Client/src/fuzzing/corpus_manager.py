"""Manage corpus."""
from __future__ import annotations

from pathlib import Path
from typing import List


class CorpusManager:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.mkdir(parents=True, exist_ok=True)

    def list_corpus(self) -> List[Path]:
        return list(self.path.glob("*") )


if __name__ == "__main__":
    manager = CorpusManager(Path("data/payloads/corpus"))
    print(manager.list_corpus())
