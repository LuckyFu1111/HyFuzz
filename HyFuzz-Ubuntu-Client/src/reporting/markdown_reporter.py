"""Render reports as Markdown."""
from __future__ import annotations

from typing import Iterable


class MarkdownReporter:
    def render(self, summary: Iterable[dict[str, str]]) -> str:
        return "\n".join(f"- {item['payload_id']}: {item['status']}" for item in summary)


if __name__ == "__main__":
    reporter = MarkdownReporter()
    print(reporter.render([{ "payload_id": "1", "status": "ok" }]))
