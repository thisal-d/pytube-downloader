"""
Centralised logging configuration for PyTube Downloader.

Usage
-----
    from utils.logger import get_logger

    logger = get_logger(__name__)
    logger.info("Starting download")
    logger.warning("Slow network detected")
    logger.error("Download failed: %s", error)

The root logger writes to both the console (WARNING+) and a rotating
file at data/logs/pytube.log (DEBUG+, up to 5 x 2 MB files).
"""

import logging
import logging.handlers
from pathlib import Path


_LOG_DIR = Path("data") / "logs"
_LOG_FILE = _LOG_DIR / "pytube.log"
_LOG_FORMAT = "%(asctime)s [%(levelname)-8s] %(name)s: %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_configured = False


def _configure() -> None:
    """Set up handlers on the root logger (called once on first use)."""
    global _configured
    if _configured:
        return

    _LOG_DIR.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    # Rotating file handler — DEBUG and above
    file_handler = logging.handlers.RotatingFileHandler(
        _LOG_FILE,
        maxBytes=2 * 1024 * 1024,  # 2 MB per file
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))

    # Console handler — WARNING and above (keeps stdout clean in production)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))

    root.addHandler(file_handler)
    root.addHandler(console_handler)

    _configured = True


def get_logger(name: str) -> logging.Logger:
    """
    Return a named logger, initialising the logging system on first call.

    Args:
        name (str): Typically ``__name__`` of the calling module.

    Returns:
        logging.Logger: Configured logger instance.
    """
    _configure()
    return logging.getLogger(name)
