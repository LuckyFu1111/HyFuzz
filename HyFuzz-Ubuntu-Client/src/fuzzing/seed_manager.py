"""Manage seeds."""
from __future__ import annotations

from typing import List


class SeedManager:
    def load(self, path: str) -> List[str]:
        with open(path, "r", encoding="utf-8") as handle:
            return [line.strip() for line in handle if line.strip()]


if __name__ == "__main__":
    manager = SeedManager()
    print(manager.load("data/payloads/fuzzing_seeds.txt"))
