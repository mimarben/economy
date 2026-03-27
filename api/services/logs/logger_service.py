import os
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

def setup_logger(name=None):
    log_dir = "logs"
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Prevent duplicate handlers
    if not logger.handlers:
        log_formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s in %(name)s: %(message)s"
        )
        
        # Try to setup file handler with daily rotation
        try:
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, f"app-{datetime.now().strftime('%Y-%m-%d')}.log")
            file_handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1)
            file_handler.suffix = "%Y-%m-%d"
            file_handler.setFormatter(log_formatter)
            logger.addHandler(file_handler)
        except (OSError, PermissionError) as e:
            # If file logging fails due to permissions or other errors, continue with console only
            print(f"Warning: Could not setup file logging: {e}")

        # Console handler for all cases
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        logger.addHandler(console_handler)

    return logger
