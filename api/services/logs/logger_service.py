"""
Logging utilities for the application.

Provides a centralized logger configuration with:
- Daily rotating file logs
- Console output
- Safe fallback if file logging fails

All modules should use `setup_logger` to ensure consistent logging behavior.
"""

import os
import logging
from logging.handlers import TimedRotatingFileHandler


def setup_logger(name: str | None = None) -> logging.Logger:
    log_dir = "logs"
    logger = logging.getLogger(name)

    if logger.hasHandlers():
        return logger

    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger.setLevel(level)

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(name)s: %(message)s"
    )

    try:
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "app.log")

        file_handler = TimedRotatingFileHandler(
            log_file,
            when="midnight",
            interval=1,
            backupCount=7
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    except (OSError, PermissionError):
        logging.basicConfig(level=level)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger
