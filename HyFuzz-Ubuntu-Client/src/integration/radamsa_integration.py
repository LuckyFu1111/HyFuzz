"""Radamsa integration stub."""
from __future__ import annotations


def build_command(seed_file: str) -> list[str]:
    return ["radamsa", seed_file]


if __name__ == "__main__":
    print(build_command("seed.txt"))
