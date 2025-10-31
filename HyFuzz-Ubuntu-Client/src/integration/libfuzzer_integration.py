"""LibFuzzer integration stub."""
from __future__ import annotations


def build_command(binary: str) -> list[str]:
    return [binary, "-runs=0"]


if __name__ == "__main__":
    print(build_command("./fuzzer"))
