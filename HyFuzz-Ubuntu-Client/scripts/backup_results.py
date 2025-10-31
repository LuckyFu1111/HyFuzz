#!/usr/bin/env python3
"""Backup results to archive."""
from pathlib import Path

from src.storage.result_archiver import ResultArchiver

if __name__ == "__main__":
    archiver = ResultArchiver(Path("data/backups/results"))
    print(archiver.archive([("demo", "ok")]))
