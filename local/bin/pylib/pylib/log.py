#!/usr/bin/env python3
import logging
import colorlog


def get_logger(name: str) -> logging.Logger:
    """Return a colorized logger for the given name."""
    logger = logging.getLogger(name)
    if not logger.handlers:  # avoid adding multiple handlers
        handler = logging.StreamHandler()
        formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(levelname)-8s%(reset)s %(name)s: %(message)s",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "blue",
                "WARNING": "green",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
    return logger
