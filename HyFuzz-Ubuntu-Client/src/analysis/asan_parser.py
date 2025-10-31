"""Parse ASAN output."""
from __future__ import annotations


class AsanParser:
    def parse(self, text: str) -> dict[str, str]:
        return {"summary": text.splitlines()[0] if text else ""}


if __name__ == "__main__":
    parser = AsanParser()
    print(parser.parse("ERROR: AddressSanitizer: heap-use-after-free"))
