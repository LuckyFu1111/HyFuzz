"""Logging helpers for the HyFuzz client."""
from __future__ import annotations

import logging
from logging import Logger
from typing import Optional


def get_logger(name: Optional[str] = None) -> Logger:
    """Return a configured logger with a sensible default format."""
    logger = logging.getLogger(name or "hyfuzz-client")
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


if __name__ == "__main__":
    log = get_logger(__name__)
    log.info("Logger bootstrap test passed.")
