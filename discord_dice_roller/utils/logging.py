"""Utilities for logging"""

# Built-in
import logging
from logging.handlers import RotatingFileHandler


# --------------------------------------------------------------------------------
# > Main
# --------------------------------------------------------------------------------
def setup_logging():
    """Setups the default logger as a file-rotating logger for info, warnings, and errors"""
    format = (
        "%(asctime)s | %(levelname)s | %(module)s.%(funcName)s:%(lineno)d | %(message)s"
    )
    handler = RotatingFileHandler("./console.log", maxBytes=100000, backupCount=10)
    date_format = "%Y-%m-%d %H:%M:%S"
    logging.basicConfig(
        handlers=[handler], level=logging.INFO, format=format, datefmt=date_format,
    )
