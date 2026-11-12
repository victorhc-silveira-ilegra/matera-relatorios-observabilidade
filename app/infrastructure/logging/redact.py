from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

SENSITIVE_KEYS = frozenset({"password", "pass", "token", "secret", "auth", "credential"})
URL_PATTERN = re.compile(r"https?://[^\s\"']+")


def sanitize_value(key: str, value: Any) -> Any:
    lowered = key.lower()
    if any(token in lowered for token in SENSITIVE_KEYS):
        return "***REDACTED***"
    if isinstance(value, str):
        return URL_PATTERN.sub(lambda m: mask_url(m.group(0)), value)
    return value


def mask_url(url: str) -> str:
    parsed = urlparse(url)
    if not parsed.netloc:
        return url
    return f"{parsed.scheme}://{parsed.netloc}/..."
