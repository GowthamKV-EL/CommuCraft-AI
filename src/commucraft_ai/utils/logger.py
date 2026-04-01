"""Logger configuration for CommuCraft-AI application.

This module provides file-based logging functionality with consistent formatting.
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional


def setup_logger(log_dir: str = "logs", log_filename: str = "app.log") -> logging.Logger:
    """
    Configure and return a logger with file-based output.

    Creates a logs directory if it doesn't exist and sets up a rotating file handler
    with both file and console output.

    Args:
        log_dir (str): Directory where log files will be stored. Defaults to "logs".
        log_filename (str): Name of the log file. Defaults to "app.log".

    Returns:
        logging.Logger: Configured logger instance ready for use.

    Errors:
        OSError: If the log directory cannot be created.
    """
    # Create logs directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    # Create logger
    logger = logging.getLogger("commucraft_ai")
    logger.setLevel(logging.DEBUG)

    # Remove existing handlers to avoid duplicates
    logger.handlers = []

    # Create formatters
    detailed_formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # File handler
    file_handler = logging.handlers.RotatingFileHandler(
        log_path / log_filename,
        maxBytes=10485760,
        backupCount=5,  # 10MB per file, keep 5 backups
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(detailed_formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance by name.

    Args:
        name (str, optional): Name of the logger. Defaults to None (returns root logger).

    Returns:
        logging.Logger: Logger instance.
    """
    if name is None:
        return logging.getLogger("commucraft_ai")
    return logging.getLogger(f"commucraft_ai.{name}")
