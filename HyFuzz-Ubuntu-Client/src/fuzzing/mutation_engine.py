"""Additional mutation strategies."""
from __future__ import annotations

from typing import List


class MutationEngine:
    def mutate(self, seed: bytes) -> List[bytes]:
        return [seed[::-1], seed + b"\x00"]


if __name__ == "__main__":
    engine = MutationEngine()
    print(engine.mutate(b"seed"))
