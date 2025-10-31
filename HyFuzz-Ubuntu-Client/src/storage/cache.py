"""In-memory cache."""
from __future__ import annotations

from typing import Dict


class Cache:
    def __init__(self) -> None:
        self._store: Dict[str, str] = {}

    def set(self, key: str, value: str) -> None:
        self._store[key] = value

    def get(self, key: str) -> str | None:
        return self._store.get(key)


if __name__ == "__main__":
    cache = Cache()
    cache.set("a", "1")
    print(cache.get("a"))
