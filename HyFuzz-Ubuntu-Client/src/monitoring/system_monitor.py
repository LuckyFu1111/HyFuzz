"""System monitoring utilities without external dependencies."""
from __future__ import annotations

import os

from .monitoring_models import SystemMetrics


def _memory_mb() -> float:
    try:
        page_size = os.sysconf("SC_PAGE_SIZE")
        with open("/proc/self/statm", "r", encoding="utf-8") as handle:
            pages = int(handle.readline().split()[0])
        return pages * page_size / (1024 * 1024)
    except (OSError, ValueError, AttributeError):
        return 0.0


class SystemMonitor:
    def snapshot(self) -> SystemMetrics:
        load = os.getloadavg()[0] if hasattr(os, "getloadavg") else 0.0
        return SystemMetrics(cpu_percent=float(load), memory_mb=_memory_mb())


if __name__ == "__main__":
    monitor = SystemMonitor()
    print(monitor.snapshot())
