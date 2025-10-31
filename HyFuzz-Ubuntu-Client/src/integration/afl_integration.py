"""AFL integration stub."""
from __future__ import annotations


def build_command(binary: str) -> list[str]:
    return ["afl-fuzz", "-i", "in", "-o", "out", "--", binary]


if __name__ == "__main__":
    print(build_command("/bin/echo"))
