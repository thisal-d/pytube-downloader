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
file at an OS-appropriate user data directory (DEBUG+, up to 5 x 2 MB
files). Falls back to console-only logging if the log directory is not
writable.
"""

import logging
import logging.handlers
import os
import platform
import threading
from pathlib import Path

_LOG_FORMAT = "%(asctime)s [%(levelname)-8s] %(name)s: %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_configured = False
_lock = threading.Lock()


def _get_user_log_dir() -> Path:
    """Return the OS-appropriate log directory."""
    system = platform.system()
    if system == "Darwin":
        return Path.home() / "Library" / "Application Support" / "PyTube Downloader" / "logs"
    elif system == "Linux":
        return Path.home() / ".local" / "share" / "PyTube Downloader" / "logs"
    else:
        return Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")) / "PyTube Downloader" / "logs"


def _configure() -> None:
    """Set up handlers on the root logger (called once on first use)."""
    global _configured
    if _configured:
        return

    with _lock:
        if _configured:
            return

        root = logging.getLogger()
        root.setLevel(logging.DEBUG)

        # File handler — try OS user data dir, fall back to project-relative, then console-only
        log_dir = _get_user_log_dir()
        log_file = log_dir / "pytube.log"
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=2 * 1024 * 1024,  # 2 MB per file
                backupCount=5,
                encoding="utf-8",
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))
            root.addHandler(file_handler)
        except (OSError, PermissionError):
            pass  # Fall back to console-only

        # Console handler — WARNING and above (keeps stdout clean in production)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))
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
