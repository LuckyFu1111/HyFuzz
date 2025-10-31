"""Archive execution results."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .file_storage import FileStorage


class ResultArchiver:
    def __init__(self, root: Path | None = None) -> None:
        self.storage = FileStorage(root or Path("data/results/successful"))

    def archive(self, rows: Iterable[tuple[str, str]]) -> list[Path]:
        paths = []
        for payload_id, output in rows:
            paths.append(self.storage.write(f"{payload_id}.txt", output))
        return paths


if __name__ == "__main__":
    archiver = ResultArchiver()
    print(archiver.archive([("1", "ok")]))
