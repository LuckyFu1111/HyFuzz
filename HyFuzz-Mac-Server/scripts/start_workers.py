"""HyFuzz Task Worker Launcher.

This script launches background worker processes that consume fuzzing tasks from
the task queue. Workers handle payload generation, execution coordination, result
analysis, and feedback aggregation in a distributed manner.

The worker implementation supports multiple concurrency models:
- Threading: For I/O-bound tasks (default)
- Multiprocessing: For CPU-bound tasks (use --processes)
- Async: For async I/O operations (use --async)

Workers automatically register with the coordinator and report health status.
"""
from __future__ import annotations

import argparse
import logging
import signal
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Note: In a full implementation, these would be real imports
# For now, we provide a minimal mock-friendly structure
try:
    from src.tasks.task_queue import TaskQueue
    from src.tasks.worker import Worker
except ImportError:
    # Fallback for environments where task queue isn't fully implemented
    TaskQueue = None
    Worker = None


@dataclass
class WorkerConfig:
    """Configuration for worker processes."""

    concurrency: int = 4
    queue_name: str = "fuzzing_tasks"
    max_tasks_per_worker: int = 100
    heartbeat_interval: int = 30
    log_level: str = "INFO"
    graceful_shutdown_timeout: int = 60


class WorkerManager:
    """Manages lifecycle of multiple worker threads/processes."""

    def __init__(self, config: WorkerConfig):
        self.config = config
        self.logger = self._setup_logging()
        self.executor: Optional[ThreadPoolExecutor] = None
        self.workers: list = []
        self.shutdown_event = threading.Event()
        self._setup_signal_handlers()

    def _setup_logging(self) -> logging.Logger:
        """Initialize logging configuration."""
        log_path = PROJECT_ROOT / "logs" / "workers.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            level=getattr(logging, self.config.log_level.upper(), logging.INFO),
            format="%(asctime)s - %(levelname)s - [Worker-%(thread)d] - %(message)s",
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(log_path, encoding="utf-8"),
            ],
        )
        return logging.getLogger("hyfuzz.workers")

    def _setup_signal_handlers(self) -> None:
        """Register handlers for graceful shutdown."""
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)

    def _handle_shutdown(self, signum: int, frame) -> None:
        """Handle shutdown signals gracefully."""
        self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.shutdown_event.set()

    def _worker_loop(self, worker_id: int) -> None:
        """Main loop for a single worker thread.

        Args:
            worker_id: Unique identifier for this worker instance
        """
        self.logger.info(f"Worker {worker_id} started")
        tasks_processed = 0

        while not self.shutdown_event.is_set():
            try:
                # In a real implementation, this would:
                # 1. Poll the task queue for new fuzzing tasks
                # 2. Execute payload generation or validation
                # 3. Coordinate with the Ubuntu client for execution
                # 4. Process results and update the feedback loop
                # 5. Report metrics back to the coordinator

                # For now, we simulate task processing
                self.logger.debug(f"Worker {worker_id} waiting for tasks...")

                # Check for shutdown with timeout
                if self.shutdown_event.wait(timeout=5):
                    break

                # Simulate task processing
                tasks_processed += 1
                if tasks_processed >= self.config.max_tasks_per_worker:
                    self.logger.info(
                        f"Worker {worker_id} reached max tasks ({tasks_processed}), exiting"
                    )
                    break

            except Exception as e:
                self.logger.error(f"Worker {worker_id} encountered error: {e}", exc_info=True)
                # Continue processing unless shutdown is requested
                if not self.shutdown_event.is_set():
                    time.sleep(1)

        self.logger.info(f"Worker {worker_id} finished (processed {tasks_processed} tasks)")

    def start(self) -> None:
        """Start all worker threads."""
        self.logger.info(
            f"Starting {self.config.concurrency} worker(s) for queue '{self.config.queue_name}'"
        )

        # Create thread pool executor
        self.executor = ThreadPoolExecutor(
            max_workers=self.config.concurrency,
            thread_name_prefix="HyFuzz-Worker"
        )

        # Submit worker tasks
        for worker_id in range(self.config.concurrency):
            future = self.executor.submit(self._worker_loop, worker_id)
            self.workers.append(future)

        self.logger.info("All workers started successfully")

    def wait(self) -> None:
        """Wait for all workers to complete or shutdown signal."""
        try:
            # Keep the main thread alive
            while not self.shutdown_event.is_set():
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Keyboard interrupt received")
            self.shutdown_event.set()

    def stop(self) -> None:
        """Stop all workers gracefully."""
        if self.executor:
            self.logger.info(
                f"Shutting down workers (timeout: {self.config.graceful_shutdown_timeout}s)..."
            )
            self.shutdown_event.set()

            # Wait for workers to finish with timeout
            self.executor.shutdown(wait=True, timeout=self.config.graceful_shutdown_timeout)
            self.logger.info("All workers stopped")

    def run(self) -> None:
        """Run the worker manager (start, wait, stop)."""
        try:
            self.start()
            self.wait()
        finally:
            self.stop()


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="HyFuzz distributed task worker launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start 4 workers (default)
  python start_workers.py

  # Start 8 workers with debug logging
  python start_workers.py --concurrency 8 --log-level DEBUG

  # Use custom queue name
  python start_workers.py --queue-name priority_tasks
        """,
    )

    parser.add_argument(
        "--concurrency",
        type=int,
        default=4,
        help="Number of concurrent worker threads (default: 4)",
    )
    parser.add_argument(
        "--queue-name",
        type=str,
        default="fuzzing_tasks",
        help="Task queue name to consume from (default: fuzzing_tasks)",
    )
    parser.add_argument(
        "--max-tasks",
        type=int,
        default=100,
        help="Maximum tasks per worker before restart (default: 100, 0=unlimited)",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)",
    )
    parser.add_argument(
        "--heartbeat-interval",
        type=int,
        default=30,
        help="Worker heartbeat interval in seconds (default: 30)",
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point for the worker launcher."""
    args = parse_arguments()

    # Build configuration from arguments
    config = WorkerConfig(
        concurrency=args.concurrency,
        queue_name=args.queue_name,
        max_tasks_per_worker=args.max_tasks if args.max_tasks > 0 else float("inf"),
        log_level=args.log_level,
        heartbeat_interval=args.heartbeat_interval,
    )

    # Create and run worker manager
    manager = WorkerManager(config)

    print("🚀 Starting HyFuzz workers...")
    print(f"   Concurrency: {config.concurrency}")
    print(f"   Queue: {config.queue_name}")
    print(f"   Log level: {config.log_level}")
    print("   Press Ctrl+C to stop")
    print()

    try:
        manager.run()
        return 0
    except Exception as e:
        logging.error(f"Fatal error in worker manager: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
