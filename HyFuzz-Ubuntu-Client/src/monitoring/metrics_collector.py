"""Collect metrics for reporting."""
from __future__ import annotations

from typing import Dict

from .resource_monitor import ResourceMonitor


class MetricsCollector:
    def __init__(self) -> None:
        self.monitor = ResourceMonitor()

    def collect(self) -> Dict[str, float]:
        return self.monitor.snapshot()


if __name__ == "__main__":
    collector = MetricsCollector()
    print(collector.collect())
