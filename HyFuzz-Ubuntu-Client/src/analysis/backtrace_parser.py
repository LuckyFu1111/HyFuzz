"""Backtrace parsing."""
from __future__ import annotations


class BacktraceParser:
    def parse(self, trace: str) -> list[str]:
        return [frame.strip() for frame in trace.split("->") if frame]


if __name__ == "__main__":
    parser = BacktraceParser()
    print(parser.parse("main->foo->bar"))
