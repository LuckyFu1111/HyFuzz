"""Define fuzzing strategies."""
from __future__ import annotations

from typing import List


class FuzzingStrategies:
    def available(self) -> List[str]:
        return ["mutational", "generation"]


if __name__ == "__main__":
    strategies = FuzzingStrategies()
    print(strategies.available())
