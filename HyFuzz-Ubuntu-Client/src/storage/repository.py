"""Repository abstraction."""
from __future__ import annotations

from typing import Iterable

from .database import execute


def save_results(rows: Iterable[tuple[str, str]]) -> None:
    execute("CREATE TABLE IF NOT EXISTS results(payload_id TEXT, output TEXT)")
    for payload_id, output in rows:
        execute("INSERT INTO results(payload_id, output) VALUES(?, ?)", (payload_id, output))


if __name__ == "__main__":
    save_results([("1", "ok")])
    print(execute("SELECT * FROM results"))
