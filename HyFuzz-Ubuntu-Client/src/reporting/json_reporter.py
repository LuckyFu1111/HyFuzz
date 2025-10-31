"""Render reports as JSON."""
from __future__ import annotations

import json
from typing import Iterable


class JSONReporter:
    def render(self, summary: Iterable[dict[str, str]]) -> str:
        return json.dumps(list(summary))


if __name__ == "__main__":
    reporter = JSONReporter()
    print(reporter.render([{ "payload_id": "1", "status": "ok" }]))
