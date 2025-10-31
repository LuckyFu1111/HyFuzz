"""Coverage analysis helper."""
from __future__ import annotations


class CoverageAnalyzer:
    def analyse(self, coverage_data: str) -> int:
        return len(coverage_data.split()) if coverage_data else 0


if __name__ == "__main__":
    analyzer = CoverageAnalyzer()
    print(analyzer.analyse("block1 block2"))
