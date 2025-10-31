"""Monitor syscalls."""
from __future__ import annotations

from typing import List

from .instrumentation_models import TraceEvent


class SyscallMonitor:
    def __init__(self) -> None:
        self.events: List[TraceEvent] = []

    def record(self, name: str, data: dict[str, str]) -> None:
        self.events.append(TraceEvent(name=name, data=data))

    def reset(self) -> None:
        self.events.clear()


if __name__ == "__main__":
    monitor = SyscallMonitor()
    monitor.record("open", {"file": "demo"})
    print(monitor.events)
