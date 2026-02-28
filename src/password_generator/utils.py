"""Utility functions for password generator."""

import logging
import sys
import time
from typing import Optional

import psutil


def setup_logging(level: int = logging.INFO, log_file: Optional[str] = None) -> None:
    """Configure logging for the application.

    Args:
        level: Logging level (default: INFO).
        log_file: Optional file path for logging output.
    """
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        handlers.append(file_handler)

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )


def check_cpu_usage(max_percent: float = 80.0, sleep_time: float = 2.0) -> bool:
    """Check CPU usage and pause if it exceeds threshold.

    Args:
        max_percent: Maximum acceptable CPU usage percentage.
        sleep_time: Seconds to sleep if usage is high.

    Returns:
        True if CPU usage was within limits, False if throttled.
    """
    try:
        cpu_usage = psutil.cpu_percent(interval=0.1)
        if cpu_usage > max_percent:
            logging.getLogger(__name__).warning(
                f"High CPU usage detected: {cpu_usage:.1f}%%. Pausing for {sleep_time}s."
            )
            time.sleep(sleep_time)
            return False
        return True
    except Exception as e:
        logging.getLogger(__name__).error(f"Error checking CPU usage: {e}")
        return True


class CpuMonitor:
    """Context manager for monitoring CPU usage during operations."""

    def __init__(self, max_percent: float = 80.0, sleep_time: float = 2.0):
        """Initialize CPU monitor.

        Args:
            max_percent: Maximum acceptable CPU usage percentage.
            sleep_time: Seconds to sleep if usage is high.
        """
        self.max_percent = max_percent
        self.sleep_time = sleep_time
        self.logger = logging.getLogger(__name__)

    def __enter__(self) -> "CpuMonitor":
        """Enter context."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context."""
        pass

    def throttle_if_needed(self) -> bool:
        """Check and throttle if CPU usage is too high.

        Returns:
            True if within limits, False if throttled.
        """
        return check_cpu_usage(self.max_percent, self.sleep_time)
