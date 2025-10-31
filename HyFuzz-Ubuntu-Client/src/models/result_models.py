"""Result models."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class CrashSummary:
    payload_id: str
    reason: str
    metadata: Dict[str, str]


if __name__ == "__main__":
    summary = CrashSummary(payload_id="1", reason="segfault", metadata={"signal": "11"})
    print(summary)
