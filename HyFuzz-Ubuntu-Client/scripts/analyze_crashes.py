#!/usr/bin/env python3
"""Print stored crash summaries."""
from src.storage.crash_storage import CrashStorage

if __name__ == "__main__":
    storage = CrashStorage()
    print(storage.list_crashes())
