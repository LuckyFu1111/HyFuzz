"""Message parsing helpers."""
from __future__ import annotations

import json
from typing import Any, Dict


def parse_message(data: bytes) -> Dict[str, Any]:
    return json.loads(data.decode("utf-8"))


if __name__ == "__main__":
    print(parse_message(b'{"hello": "world"}'))
