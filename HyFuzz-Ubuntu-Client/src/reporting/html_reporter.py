"""Render reports as HTML."""
from __future__ import annotations

from typing import Iterable


class HTMLReporter:
    def render(self, summary: Iterable[dict[str, str]]) -> str:
        rows = "".join(f"<li>{item['payload_id']}: {item['status']}</li>" for item in summary)
        return f"<ul>{rows}</ul>"


if __name__ == "__main__":
    reporter = HTMLReporter()
    print(reporter.render([{ "payload_id": "1", "status": "ok" }]))
