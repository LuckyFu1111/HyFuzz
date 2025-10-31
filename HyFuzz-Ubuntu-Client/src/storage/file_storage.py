"""File storage helpers."""
from __future__ import annotations

from pathlib import Path


class FileStorage:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def write(self, name: str, content: str) -> Path:
        path = self.root / name
        path.write_text(content, encoding="utf-8")
        return path


if __name__ == "__main__":
    storage = FileStorage(Path("./tmp"))
    print(storage.write("demo.txt", "hello"))
