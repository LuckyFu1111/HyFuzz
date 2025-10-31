"""Utility helpers for the MCP client."""
from __future__ import annotations

import json
from typing import Any, Dict


def serialize_message(payload: Dict[str, Any]) -> bytes:
    return json.dumps(payload).encode("utf-8")


if __name__ == "__main__":
    print(serialize_message({"ping": "pong"}))
