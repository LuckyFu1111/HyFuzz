"""Parse Valgrind output."""
from __future__ import annotations


class ValgrindParser:
    def parse(self, text: str) -> dict[str, int]:
        leaks = text.count("definitely lost")
        return {"definitely_lost": leaks}


if __name__ == "__main__":
    parser = ValgrindParser()
    print(parser.parse("==123== definitely lost: 0 bytes"))
