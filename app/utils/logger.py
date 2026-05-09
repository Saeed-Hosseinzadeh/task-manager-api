"""
Logging Configuration

This module configures the application's logging system using Python's built-in
logging library. It sets up both console and rotating file handlers to ensure
logs are persisted while maintaining manageable log file sizes.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


# Directory where log files will be stored
LOG_DIR = Path("logs")

# Main log file path
LOG_FILE = LOG_DIR / "app.log"

# Create log directory if it does not exist
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Create and configure the main application logger
logger = logging.getLogger("task_manager")
logger.setLevel(logging.INFO)

# Prevent duplicate log entries from parent loggers
logger.propagate = False

# Standard log message format
formatter = logging.Formatter(
    fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# File handler with automatic log rotation
file_handler = RotatingFileHandler(
    filename=LOG_FILE,
    maxBytes=5 * 1024 * 1024,  # Maximum size of each log file (5 MB)
    backupCount=3,             # Number of backup log files to retain
    encoding="utf-8"
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

# Console handler for development-time log visibility
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# Attach handlers only if they have not already been added
# This prevents duplicate logs when modules are reloaded
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
