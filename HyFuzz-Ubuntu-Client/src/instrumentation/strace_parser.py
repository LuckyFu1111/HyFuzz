"""Parse strace output."""
from __future__ import annotations

from typing import List


class StraceParser:
    def parse(self, lines: List[str]) -> List[str]:
        return [line.split("(")[0] for line in lines]


if __name__ == "__main__":
    parser = StraceParser()
    print(parser.parse(["open(\"file\")", "read(\"fd\")"]))
