#!/usr/bin/env python3
"""HyFuzz Task Worker Stopper.

This script gracefully stops running HyFuzz worker processes.
It sends shutdown signals to workers and waits for them to complete
their current tasks before terminating.

Usage:
    python stop_workers.py              # Stop all workers gracefully
    python stop_workers.py --force      # Force stop workers immediately
    python stop_workers.py --timeout 30 # Wait up to 30 seconds for graceful shutdown
"""
from __future__ import annotations

import argparse
import logging
import os
import signal
import sys
import time
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
logger = logging.getLogger("hyfuzz.stop_workers")


class WorkerStopper:
    """Manages graceful shutdown of worker processes."""

    def __init__(self, timeout: int = 60, force: bool = False):
        """Initialize worker stopper.

        Args:
            timeout: Maximum seconds to wait for graceful shutdown
            force: If True, forcefully kill workers without waiting
        """
        self.timeout = timeout
        self.force = force
        self.pid_file = PROJECT_ROOT / "data" / "workers.pid"

    def get_worker_pids(self) -> List[int]:
        """Get list of worker process IDs.

        Returns:
            List of worker PIDs
        """
        pids = []

        # Try to read PID file
        if self.pid_file.exists():
            try:
                with open(self.pid_file, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and line.isdigit():
                            pids.append(int(line))
                logger.info(f"Found {len(pids)} worker PIDs in {self.pid_file}")
            except Exception as e:
                logger.warning(f"Failed to read PID file: {e}")

        # Also try to find workers by process name
        try:
            import psutil

            for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                try:
                    cmdline = proc.info.get("cmdline", [])
                    if cmdline and any("start_workers.py" in arg for arg in cmdline):
                        pid = proc.info["pid"]
                        if pid not in pids:
                            pids.append(pid)
                            logger.info(f"Found worker process by name: PID {pid}")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except ImportError:
            logger.debug("psutil not available, skipping process name search")

        return pids

    def is_process_running(self, pid: int) -> bool:
        """Check if a process is running.

        Args:
            pid: Process ID to check

        Returns:
            True if process is running, False otherwise
        """
        try:
            os.kill(pid, 0)  # Signal 0 just checks if process exists
            return True
        except (OSError, ProcessLookupError):
            return False

    def stop_worker(self, pid: int) -> bool:
        """Stop a single worker process.

        Args:
            pid: Process ID to stop

        Returns:
            True if successfully stopped, False otherwise
        """
        if not self.is_process_running(pid):
            logger.info(f"Worker {pid} is not running")
            return True

        try:
            if self.force:
                # Force kill immediately
                logger.warning(f"Force killing worker {pid}")
                os.kill(pid, signal.SIGKILL)
                return True
            else:
                # Graceful shutdown - send SIGTERM
                logger.info(f"Sending SIGTERM to worker {pid}")
                os.kill(pid, signal.SIGTERM)

                # Wait for process to terminate
                start_time = time.time()
                while time.time() - start_time < self.timeout:
                    if not self.is_process_running(pid):
                        logger.info(f"Worker {pid} stopped gracefully")
                        return True
                    time.sleep(0.5)

                # Timeout reached, force kill
                logger.warning(
                    f"Worker {pid} did not stop within {self.timeout}s, force killing"
                )
                os.kill(pid, signal.SIGKILL)
                time.sleep(0.5)

                if not self.is_process_running(pid):
                    logger.info(f"Worker {pid} force killed")
                    return True
                else:
                    logger.error(f"Failed to stop worker {pid}")
                    return False

        except Exception as e:
            logger.error(f"Error stopping worker {pid}: {e}")
            return False

    def stop_all_workers(self) -> int:
        """Stop all worker processes.

        Returns:
            Number of workers successfully stopped
        """
        pids = self.get_worker_pids()

        if not pids:
            logger.info("No worker processes found")
            return 0

        logger.info(f"Stopping {len(pids)} worker process(es)...")

        stopped_count = 0
        for pid in pids:
            if self.stop_worker(pid):
                stopped_count += 1

        # Clean up PID file
        if self.pid_file.exists():
            try:
                self.pid_file.unlink()
                logger.info(f"Removed PID file: {self.pid_file}")
            except Exception as e:
                logger.warning(f"Failed to remove PID file: {e}")

        return stopped_count


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Stop HyFuzz worker processes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="Maximum seconds to wait for graceful shutdown (default: 60)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force kill workers immediately without graceful shutdown",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Create stopper and stop workers
    stopper = WorkerStopper(timeout=args.timeout, force=args.force)

    try:
        stopped_count = stopper.stop_all_workers()

        if stopped_count > 0:
            logger.info(f"✓ Successfully stopped {stopped_count} worker(s)")
            return 0
        else:
            logger.warning("No workers were stopped")
            return 1

    except KeyboardInterrupt:
        logger.warning("Interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Failed to stop workers: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
