#!/usr/bin/env python3
"""HyFuzz System Restore Script.

Restore HyFuzz system from backup.

Usage:
    python restore_system.py backup_file.tar.gz
    python restore_system.py backup_dir/
"""
import argparse
import logging
import shutil
import sys
import tarfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger("hyfuzz.restore")

def restore_from_archive(archive_path: Path) -> bool:
    """Restore from compressed backup."""
    temp_dir = PROJECT_ROOT / "temp_restore"
    temp_dir.mkdir(exist_ok=True)

    try:
        logger.info(f"Extracting {archive_path}...")
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(temp_dir)

        # Find extracted directory
        extracted = list(temp_dir.iterdir())[0]
        return restore_from_directory(extracted)
    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

def restore_from_directory(backup_dir: Path) -> bool:
    """Restore from backup directory."""
    logger.info(f"Restoring from {backup_dir}...")

    # Restore items
    items = [
        ("data", PROJECT_ROOT / "data"),
        ("config", PROJECT_ROOT / "config"),
        (".env", PROJECT_ROOT / ".env"),
        ("logs", PROJECT_ROOT / "logs"),
        ("results", PROJECT_ROOT / "results"),
    ]

    for name, dest in items:
        source = backup_dir / name
        if not source.exists():
            logger.warning(f"Skipping {name}: not in backup")
            continue

        try:
            if dest.exists():
                if dest.is_dir():
                    shutil.rmtree(dest)
                else:
                    dest.unlink()

            if source.is_dir():
                shutil.copytree(source, dest)
            else:
                shutil.copy2(source, dest)

            logger.info(f"✓ Restored {name}")
        except Exception as e:
            logger.error(f"Failed to restore {name}: {e}")
            return False

    return True

def main():
    parser = argparse.ArgumentParser(description="Restore HyFuzz from backup")
    parser.add_argument("backup", type=Path, help="Backup file or directory")
    args = parser.parse_args()

    if not args.backup.exists():
        print(f"✗ Backup not found: {args.backup}")
        return 1

    try:
        if args.backup.is_file():
            success = restore_from_archive(args.backup)
        else:
            success = restore_from_directory(args.backup)

        if success:
            print("\n✓ System restored successfully!")
            return 0
        else:
            print("\n✗ Restore completed with errors")
            return 1
    except Exception as e:
        print(f"\n✗ Restore failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
