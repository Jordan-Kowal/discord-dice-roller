"""Utilities for logging"""

# Built-in
import logging
import os
from logging.handlers import RotatingFileHandler

# --------------------------------------------------------------------------------
# > Main
# --------------------------------------------------------------------------------
LOG_FILE = os.path.join(os.getcwd(), "console.log")


def setup_logging():
    """
    Setups 2 loggers for INFO+ message:
        1 RotatingFileHandler
        1 StreamHandler which outputs in the console
    """
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(module)s.%(funcName)s:%(lineno)d | %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )
    # RotatingFileHandler
    rotating_file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=100000, backupCount=10
    )
    rotating_file_handler.setFormatter(formatter)
    rotating_file_handler.setLevel(logging.INFO)
    # StreamHandler
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)
    # Update the config
    logging.basicConfig(
        handlers=[rotating_file_handler, stream_handler],
        level=logging.INFO,
    )
