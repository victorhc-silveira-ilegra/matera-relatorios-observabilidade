from __future__ import annotations

import logging

from app.infrastructure.logging.emit import log_event
from app.infrastructure.logging.events import (
    CLOUDWATCH_SCRAPE_FAILED,
    CLOUDWATCH_SCRAPE_SKIPPED,
    CLOUDWATCH_SCRAPE_STARTED,
    METRICS_FETCH_FAILED,
    METRICS_FETCH_STARTED,
    REPORT_GENERATION_COMPLETED,
    REPORT_GENERATION_FAILED,
    REPORT_GENERATION_STARTED,
)
from app.infrastructure.logging.formatters import (
    JsonSemanticFormatter,
    TextSemanticFormatter,
)
from app.infrastructure.logging.redact import (
    SENSITIVE_KEYS,
    URL_PATTERN,
    mask_url,
    sanitize_value,
)


def configure_logging(level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger("relatorios")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False
    return logger


__all__ = [
    "CLOUDWATCH_SCRAPE_FAILED",
    "CLOUDWATCH_SCRAPE_SKIPPED",
    "CLOUDWATCH_SCRAPE_STARTED",
    "JsonSemanticFormatter",
    "METRICS_FETCH_FAILED",
    "METRICS_FETCH_STARTED",
    "REPORT_GENERATION_COMPLETED",
    "REPORT_GENERATION_FAILED",
    "REPORT_GENERATION_STARTED",
    "SENSITIVE_KEYS",
    "TextSemanticFormatter",
    "URL_PATTERN",
    "configure_logging",
    "log_event",
    "mask_url",
    "sanitize_value",
]
