from __future__ import annotations

import json
import logging
import sys

SERVICE_NAME = "claims-service"


def get_logger() -> logging.Logger:
    """Structured JSON logs, the way they'd land in CloudWatch."""
    logger = logging.getLogger(SERVICE_NAME)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def log_json(logger: logging.Logger, level: int, payload: dict) -> None:
    logger.log(level, json.dumps({"service": SERVICE_NAME, **payload}))
