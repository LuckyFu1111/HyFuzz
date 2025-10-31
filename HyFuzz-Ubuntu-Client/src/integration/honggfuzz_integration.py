"""Honggfuzz integration stub."""
from __future__ import annotations


def build_command(binary: str) -> list[str]:
    return ["honggfuzz", "--", binary]


if __name__ == "__main__":
    print(build_command("./hfuzz"))
