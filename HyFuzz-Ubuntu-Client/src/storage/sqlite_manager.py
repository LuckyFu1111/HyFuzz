"""Higher level SQLite manager."""
from __future__ import annotations

from typing import Iterable, Tuple

from .database import execute

# Security: Allowlist of valid table names to prevent SQL injection
# Table names cannot be parameterized in SQL, so we validate against this list
ALLOWED_TABLES = frozenset({
    "demo",
    "payloads",
    "results",
    "campaigns",
    "executions",
    "defense_verdicts",
    "instrumentation_data",
})


def _validate_table_name(table: str) -> None:
    """
    Validate table name against allowlist to prevent SQL injection.

    Args:
        table: Table name to validate

    Raises:
        ValueError: If table name is not in allowlist
    """
    if table not in ALLOWED_TABLES:
        raise ValueError(
            f"Invalid table name: {table}. "
            f"Allowed tables: {', '.join(sorted(ALLOWED_TABLES))}"
        )


def fetch_all(table: str) -> list[Tuple]:
    """
    Fetch all rows from the specified table.

    Args:
        table: Table name (must be in ALLOWED_TABLES)

    Returns:
        List of tuples containing (payload_id, data)

    Raises:
        ValueError: If table name is invalid
    """
    _validate_table_name(table)
    execute(f"CREATE TABLE IF NOT EXISTS {table}(payload_id TEXT, data TEXT)")
    return execute(f"SELECT * FROM {table}")


def bulk_insert(table: str, rows: Iterable[Tuple[str, str]]) -> None:
    """
    Insert multiple rows into the specified table.

    Args:
        table: Table name (must be in ALLOWED_TABLES)
        rows: Iterable of (payload_id, data) tuples

    Raises:
        ValueError: If table name is invalid
    """
    _validate_table_name(table)
    execute(f"CREATE TABLE IF NOT EXISTS {table}(payload_id TEXT, data TEXT)")
    for row in rows:
        execute(f"INSERT INTO {table}(payload_id, data) VALUES(?, ?)", row)


if __name__ == "__main__":
    bulk_insert("demo", [("1", "data")])
    print(fetch_all("demo"))
