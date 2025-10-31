"""Peach integration stub."""
from __future__ import annotations


def build_command(model: str) -> list[str]:
    return ["peach", model]


if __name__ == "__main__":
    print(build_command("model.xml"))
