"""Deduplicate crashes."""
from __future__ import annotations

from typing import Iterable, List


class Deduplicator:
    def deduplicate(self, crashes: Iterable[str]) -> List[str]:
        seen = set()
        unique = []
        for crash in crashes:
            if crash not in seen:
                seen.add(crash)
                unique.append(crash)
        return unique


if __name__ == "__main__":
    deduplicator = Deduplicator()
    print(deduplicator.deduplicate(["a", "b", "a"]))
