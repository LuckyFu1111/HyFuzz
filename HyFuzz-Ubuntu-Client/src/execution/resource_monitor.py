"""Resource monitoring utilities using /proc data."""
from __future__ import annotations

import os


class ResourceMonitor:
    @staticmethod
    def _memory_mb() -> float:
        try:
            page_size = os.sysconf("SC_PAGE_SIZE")
            with open("/proc/self/statm", "r", encoding="utf-8") as handle:
                pages = int(handle.readline().split()[0])
            return pages * page_size / (1024 * 1024)
        except (OSError, ValueError, AttributeError):
            return 0.0

    def snapshot(self) -> dict[str, float]:
        load = os.getloadavg()[0] if hasattr(os, "getloadavg") else 0.0
        return {"cpu_percent": float(load), "memory_mb": self._memory_mb()}


if __name__ == "__main__":
    print(ResourceMonitor().snapshot())
