"""Protocol utilities."""
from __future__ import annotations


def describe(protocol: str) -> str:
    return f"Handler for {protocol.upper()}"


if __name__ == "__main__":
    print(describe("coap"))
