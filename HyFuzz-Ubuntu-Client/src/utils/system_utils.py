"""System level helpers."""
from __future__ import annotations

import os
import platform
from typing import Dict


def system_facts() -> Dict[str, str]:
    return {"platform": platform.system(), "release": platform.release(), "user": os.getenv("USER", "unknown")}


if __name__ == "__main__":
    print(system_facts())
