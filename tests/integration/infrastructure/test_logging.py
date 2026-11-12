from __future__ import annotations

import json
import logging

import pytest
from app.infrastructure.logging import (
    JsonSemanticFormatter,
    TextSemanticFormatter,
    configure_logging,
    log_event,
    mask_url,
    sanitize_value,
)


def test_logging_and_sanitization(caplog: pytest.LogCaptureFixture) -> None:
    assert sanitize_value("password", "secret123") == "***REDACTED***"
    assert sanitize_value("url", "https://secret.host.local/path?a=1") == "https://secret.host.local/..."
    assert sanitize_value("count", 42) == 42
    assert mask_url("not-a-url") == "not-a-url"

    logger = configure_logging(logging.INFO)
    logger = configure_logging(logging.INFO)
    with caplog.at_level(logging.INFO, logger="relatorios"):
        logger.propagate = True
        log_event(logger, logging.INFO, "test.event.fired", password="abc", endpoint="https://a.b/c")
    assert "***REDACTED***" in caplog.text
    assert "https://a.b/..." in caplog.text


def test_formatters() -> None:
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="plain message",
        args=(),
        exc_info=None,
    )
    json_fmt = JsonSemanticFormatter()
    payload = json.loads(json_fmt.format(record))
    assert payload["level"] == "INFO"
    assert payload["event"] == "plain message"

    try:
        raise ValueError("simulated error")
    except ValueError:
        import sys

        record.exc_info = sys.exc_info()

    formatted_json_exc = json_fmt.format(record)
    assert "simulated error" in formatted_json_exc

    text_fmt = TextSemanticFormatter()
    text_out = text_fmt.format(record)
    assert "event=plain message" in text_out

    semantic_record = logging.LogRecord(
        name="test",
        level=logging.WARNING,
        pathname="test.py",
        lineno=2,
        msg="fallback",
        args=(),
        exc_info=None,
    )
    semantic_record.semantic = {"event": "custom.event", "k1": "v1"}
    assert "event=custom.event" in text_fmt.format(semantic_record)
    assert "k1=v1" in text_fmt.format(semantic_record)
