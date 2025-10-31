#!/usr/bin/env python3
"""Display system metrics."""
from src.monitoring.system_monitor import SystemMonitor

if __name__ == "__main__":
    monitor = SystemMonitor()
    print(monitor.snapshot())
