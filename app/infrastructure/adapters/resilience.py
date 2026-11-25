from __future__ import annotations

import logging
from collections.abc import Callable
from typing import TypeVar

import httpx

from app.infrastructure.logging import METRICS_FETCH_FAILED, log_event

T = TypeVar("T")


def describe_error(exc: Exception) -> str:
    if isinstance(exc, httpx.HTTPStatusError):
        status = exc.response.status_code
        detail = ""
        try:
            body = exc.response.json()
            results = body.get("results", {})
            if isinstance(results, dict):
                first: object = next(iter(results.values()), {})
                if isinstance(first, dict) and first.get("error"):
                    detail = str(first["error"])
        except Exception:
            detail = exc.response.text.strip()[:200]
        return f"HTTP {status} ({detail})" if detail else f"HTTP {status}"
    if isinstance(exc, httpx.TimeoutException):
        return f"timeout ({exc})"
    if isinstance(exc, httpx.RequestError):
        return f"erro de conexão ({exc})"
    return str(exc) or type(exc).__name__


def safe_collect(
    scope: str,
    client_name: str,
    fn: Callable[[], T],
    default: T,
    warnings: list[str],
    logger: logging.Logger | None = None,
) -> T:
    try:
        return fn()
    except Exception as exc:
        reason = describe_error(exc)
        msg = f"Não foi possível gerar dashboard de {scope} no cliente {client_name} por {reason}."
        if msg not in warnings:
            warnings.append(msg)
        if logger is not None:
            log_event(
                logger,
                logging.WARNING,
                METRICS_FETCH_FAILED,
                client=client_name,
                scope=scope,
                reason=reason,
            )
        return default
