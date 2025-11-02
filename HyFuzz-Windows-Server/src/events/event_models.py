"""Event models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Dict, Any


@dataclass
class Event:
    name: str
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


if __name__ == "__main__":
    print(Event(name="demo", payload={}))
