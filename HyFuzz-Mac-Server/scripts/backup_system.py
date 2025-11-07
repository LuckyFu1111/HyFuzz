#!/usr/bin/env python3
"""HyFuzz System Backup Script.

This script creates backups of the HyFuzz system including:
- Database
- Configuration files
- User data
- Logs (optional)
- Results (optional)

Usage:
    python backup_system.py                    # Create full backup
    python backup_system.py --no-logs          # Backup without logs
    python backup_system.py --output /backups  # Custom backup location
"""
from __future__ import annotations

import argparse
import json
import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("hyfuzz.backup")


class SystemBackup:
    """Manages system backups."""

    def __init__(
        self,
        output_dir: Optional[Path] = None,
        include_logs: bool = True,
        include_results: bool = True,
        compress: bool = True,
    ):
        self.output_dir = output_dir or PROJECT_ROOT / "backups"
        self.include_logs = include_logs
        self.include_results = include_results
        self.compress = compress
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self) -> Path:
        """Create system backup."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"hyfuzz_backup_{timestamp}"
        backup_dir = self.output_dir / backup_name

        logger.info(f"Creating backup: {backup_name}")

        backup_dir.mkdir(parents=True, exist_ok=True)

        # Backup items
        items_to_backup = [
            ("database", PROJECT_ROOT / "data"),
            ("config", PROJECT_ROOT / "config"),
            (".env", PROJECT_ROOT / ".env"),
        ]

        if self.include_logs:
            items_to_backup.append(("logs", PROJECT_ROOT / "logs"))
        if self.include_results:
            items_to_backup.append(("results", PROJECT_ROOT / "results"))

        for name, source in items_to_backup:
            if not source.exists():
                logger.warning(f"Skipping {name}: not found")
                continue

            dest = backup_dir / name
            try:
                if source.is_dir():
                    shutil.copytree(source, dest)
                else:
                    shutil.copy2(source, dest)
                logger.info(f"✓ Backed up {name}")
            except Exception as e:
                logger.warning(f"Failed to backup {name}: {e}")

        # Compress
        if self.compress:
            logger.info("Compressing...")
            shutil.make_archive(str(self.output_dir / backup_name), "gztar", backup_dir)
            shutil.rmtree(backup_dir)
            final_path = self.output_dir / f"{backup_name}.tar.gz"
        else:
            final_path = backup_dir

        logger.info(f"✓ Backup created: {final_path}")
        return final_path


def main():
    parser = argparse.ArgumentParser(description="Backup HyFuzz system")
    parser.add_argument("--output", "-o", type=Path, help="Output directory")
    parser.add_argument("--no-logs", action="store_true", help="Exclude logs")
    parser.add_argument("--no-results", action="store_true", help="Exclude results")
    parser.add_argument("--no-compress", action="store_true", help="No compression")
    args = parser.parse_args()

    backup = SystemBackup(
        output_dir=args.output,
        include_logs=not args.no_logs,
        include_results=not args.no_results,
        compress=not args.no_compress,
    )

    try:
        backup_path = backup.create_backup()
        print(f"\n✓ Backup created: {backup_path}")
        return 0
    except Exception as e:
        print(f"\n✗ Backup failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
