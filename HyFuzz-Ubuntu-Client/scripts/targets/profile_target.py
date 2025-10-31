#!/usr/bin/env python3
"""Profile a single target."""
from src.targets.target_profiler import TargetProfiler

if __name__ == "__main__":
    profiler = TargetProfiler()
    print(profiler.profile({"host": "localhost", "port": 5683, "protocol": "coap"}))
