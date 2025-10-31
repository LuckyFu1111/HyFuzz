"""General purpose helper functions."""
from __future__ import annotations

from typing import Any, Dict


def flatten_dict(data: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in data.items():
        new_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            result.update(flatten_dict(value, new_key))
        else:
            result[new_key] = value
    return result


if __name__ == "__main__":
    print(flatten_dict({"a": {"b": 1}}))
