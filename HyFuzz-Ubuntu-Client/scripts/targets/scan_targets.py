#!/usr/bin/env python3
"""Scan targets from configuration."""
from src.targets.target_scanner import TargetScanner

if __name__ == "__main__":
    scanner = TargetScanner()
    print(scanner.scan())
