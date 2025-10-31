"""Simple SQLite database helper."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable, Tuple

_DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "database" / "client.db"
_DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def execute(query: str, params: Iterable[object] | None = None) -> list[Tuple]:
    with sqlite3.connect(_DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(query, tuple(params or ()))
        conn.commit()
        return cur.fetchall()


if __name__ == "__main__":
    execute("CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, value TEXT)")
    execute("INSERT OR REPLACE INTO kv(key, value) VALUES(?, ?)", ("demo", "1"))
    print(execute("SELECT * FROM kv"))
