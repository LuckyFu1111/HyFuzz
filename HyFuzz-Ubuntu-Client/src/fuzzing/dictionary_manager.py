"""Manage fuzzing dictionaries."""
from __future__ import annotations

from typing import List


class DictionaryManager:
    def load(self, entries: List[str]) -> List[str]:
        return [entry.upper() for entry in entries]


if __name__ == "__main__":
    manager = DictionaryManager()
    print(manager.load(["test"]))
