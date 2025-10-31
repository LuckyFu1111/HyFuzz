"""Parse ltrace output."""
from __future__ import annotations

from typing import List


class LtraceParser:
    def parse(self, lines: List[str]) -> List[str]:
        return [line.split("(")[0] for line in lines]


if __name__ == "__main__":
    parser = LtraceParser()
    print(parser.parse(["puts(\"hi\")"]))
