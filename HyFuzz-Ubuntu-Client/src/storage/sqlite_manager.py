"""Higher level SQLite manager."""
from __future__ import annotations

from typing import Iterable, Tuple

from .database import execute


def fetch_all(table: str) -> list[Tuple]:
    execute(f"CREATE TABLE IF NOT EXISTS {table}(payload_id TEXT, data TEXT)")
    return execute(f"SELECT * FROM {table}")


def bulk_insert(table: str, rows: Iterable[Tuple[str, str]]) -> None:
    execute(f"CREATE TABLE IF NOT EXISTS {table}(payload_id TEXT, data TEXT)")
    for row in rows:
        execute(f"INSERT INTO {table}(payload_id, data) VALUES(?, ?)", row)


if __name__ == "__main__":
    bulk_insert("demo", [("1", "data")])
    print(fetch_all("demo"))
