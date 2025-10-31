"""Analysis models."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class CrashAnalysis:
    payload_id: str
    stack_trace: List[str]
    exploitable: bool


if __name__ == "__main__":
    print(CrashAnalysis("1", ["main"], False))
