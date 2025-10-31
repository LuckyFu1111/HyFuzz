"""Monitoring models."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SystemMetrics:
    cpu_percent: float
    memory_mb: float


if __name__ == "__main__":
    print(SystemMetrics(cpu_percent=1.0, memory_mb=50.0))
