"""Aggregate resource metrics."""
from __future__ import annotations

from .system_monitor import SystemMonitor


class ResourceMonitor:
    def __init__(self) -> None:
        self.system_monitor = SystemMonitor()

    def snapshot(self) -> dict[str, float]:
        metrics = self.system_monitor.snapshot()
        return {"cpu_percent": metrics.cpu_percent, "memory_mb": metrics.memory_mb}


if __name__ == "__main__":
    monitor = ResourceMonitor()
    print(monitor.snapshot())
