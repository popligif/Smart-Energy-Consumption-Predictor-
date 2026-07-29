"""
System-wide logging configuration.
"""
import os
import logging

LOG_FILE = os.path.join(os.path.dirname(__file__), "app.log")

def setup_logging() -> None:
    """Sets up log formats, writing to stdout and a local configuration log file."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    logger.info("Logging configured successfully.")
