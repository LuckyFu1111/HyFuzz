"""Process utilities without external dependencies."""
from __future__ import annotations

from pathlib import Path


def process_running(name: str) -> bool:
    proc_dir = Path("/proc")
    if not proc_dir.exists():
        return False
    for entry in proc_dir.iterdir():
        if not entry.is_dir() or not entry.name.isdigit():
            continue
        try:
            cmdline = (entry / "cmdline").read_text(encoding="utf-8")
        except OSError:
            continue
        if name.lower() in cmdline.lower():
            return True
    return False


if __name__ == "__main__":
    print("Is python running?", process_running("python"))
