"""Simple fuzzing helpers."""
from __future__ import annotations

from typing import List


def mutate(seed: bytes) -> List[bytes]:
    return [seed[::-1], seed + b"!", seed.upper()]


if __name__ == "__main__":
    print(mutate(b"hello"))
