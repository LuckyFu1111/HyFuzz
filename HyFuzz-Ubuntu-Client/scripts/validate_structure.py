"""Utility script to verify the Phase 3 directory structure for the Ubuntu client."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve().parent.parent


EXPECTED_PATHS: tuple[Path, ...] = (
    PROJECT_ROOT / "src" / "targets",
    PROJECT_ROOT / "src" / "instrumentation",
    PROJECT_ROOT / "src" / "analysis",
    PROJECT_ROOT / "src" / "reporting",
    PROJECT_ROOT / "src" / "monitoring",
    PROJECT_ROOT / "src" / "notifications",
    PROJECT_ROOT / "src" / "scheduling",
    PROJECT_ROOT / "src" / "fuzzing",
    PROJECT_ROOT / "src" / "integration",
    PROJECT_ROOT / "tests" / "e2e",
    PROJECT_ROOT / "data" / "payloads" / "corpus",
    PROJECT_ROOT / "data" / "results" / "coverage",
    PROJECT_ROOT / "data" / "results" / "crashes",
    PROJECT_ROOT / "data" / "results" / "successful",
    PROJECT_ROOT / "data" / "results" / "failed",
    PROJECT_ROOT / "data" / "results" / "statistics",
    PROJECT_ROOT / "config" / "example_configs",
    PROJECT_ROOT / "docs" / "images",
)


def find_missing(paths: Iterable[Path]) -> list[Path]:
    """Return a list of missing paths from the provided iterable."""
    return [path for path in paths if not path.exists()]


def main() -> int:
    missing = find_missing(EXPECTED_PATHS)
    if not missing:
        print("All expected Phase 3 paths are present.")
        return 0

    print("Missing paths detected:")
    for path in missing:
        print(f" - {path.relative_to(PROJECT_ROOT)}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
