"""Crash analysis models."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class CrashDetail:
    payload_id: str
    stack_trace: List[str]
    exploitable: bool


if __name__ == "__main__":
    print(CrashDetail(payload_id="1", stack_trace=["main"], exploitable=False))
