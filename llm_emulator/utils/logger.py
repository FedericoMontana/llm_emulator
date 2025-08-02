# llm_emulator/utils/logger.py

import logging
import sys


def setup_logger(name="llm_emulator", level=logging.INFO):
    """
    Sets up a structured logger.
    """
    # Prevent multiple handlers being added if called more than once
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel(level)

    # Create a handler to print to stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    # Create a formatter and set it for the handler
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - [%(levelname)s] - %(message)s"
    )
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)

    return logger


# Default logger instance
log = setup_logger()
