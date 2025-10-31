"""Models for instrumentation data."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class TraceEvent:
    name: str
    data: Dict[str, str]


if __name__ == "__main__":
    print(TraceEvent(name="syscall", data={"value": "open"}))
