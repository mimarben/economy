import os
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

def setup_logger(name=None):
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, f"app-{datetime.now().strftime('%Y-%m-%d')}.log")

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Prevent duplicate handlers
    if not logger.handlers:
        # File handler with daily rotation
        file_handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1)
        file_handler.suffix = "%Y-%m-%d"
        file_formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s in %(name)s: %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Optional: Console handler for dev
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(file_formatter)
        logger.addHandler(console_handler)

    return logger
