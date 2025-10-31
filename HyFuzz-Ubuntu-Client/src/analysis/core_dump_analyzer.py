"""Core dump parser."""
from __future__ import annotations

from pathlib import Path


class CoreDumpAnalyzer:
    def summarise(self, path: Path) -> dict[str, str]:
        return {"path": str(path), "size": str(path.stat().st_size) if path.exists() else "0"}


if __name__ == "__main__":
    analyzer = CoreDumpAnalyzer()
    print(analyzer.summarise(Path("/tmp/nonexistent")))
