"""Grammar based fuzzing."""
from __future__ import annotations

from typing import List


class GrammarFuzzer:
    def generate(self, grammar: dict[str, List[str]]) -> List[str]:
        start = grammar.get("<start>", [""])[0]
        return [start.replace("<digit>", "1")]


if __name__ == "__main__":
    fuzzer = GrammarFuzzer()
    print(fuzzer.generate({"<start>": ["ID-<digit>"]}))
