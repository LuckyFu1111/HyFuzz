"""Track code coverage."""
from __future__ import annotations

from typing import Set


class CoverageTracker:
    def __init__(self) -> None:
        self.blocks: Set[str] = set()

    def record(self, block: str) -> None:
        self.blocks.add(block)

    def reset(self) -> None:
        self.blocks.clear()


if __name__ == "__main__":
    tracker = CoverageTracker()
    tracker.record("block1")
    print(tracker.blocks)
