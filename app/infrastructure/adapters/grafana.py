from __future__ import annotations

import math
from typing import Any

import httpx

from app.domain.flagship.models import PodRestart
from app.domain.time_window import TimeWindow


def clean_float(val: float | None) -> float | None:
    if val is None or math.isnan(val) or math.isinf(val):
        return None
    return val


def extract_scalar_from_frames(frames: list[dict[str, Any]]) -> float | None:
    total = 0.0
    found = False
    for frame in frames:
        values = frame.get("data", {}).get("values", [])
        if len(values) >= 2 and values[1]:
            non_null = [float(v) for v in values[1] if v is not None]
            if non_null:
                total += non_null[-1]
                found = True
    return total if found else None


def extract_pod_restarts(frames: list[dict[str, Any]]) -> list[PodRestart]:
    restarts_by_pod: dict[str, float] = {}
    for frame in frames:
        fields = frame.get("schema", {}).get("fields", [])
        values = frame.get("data", {}).get("values", [])
        if len(fields) < 2 or len(values) < 2 or not values[1]:
            continue
        labels = fields[1].get("labels", {})
        pod_name = str(labels.get("pod") or labels.get("pod_name") or "unknown")
        val = values[1][-1]
        if val is not None and float(val) > 0:
            restarts_by_pod[pod_name] = restarts_by_pod.get(pod_name, 0.0) + float(val)

    result = [PodRestart(pod=pod, restarts=round(val, 2)) for pod, val in restarts_by_pod.items() if round(val, 2) > 0]
    result.sort(key=lambda r: r.restarts, reverse=True)
    return result


class GrafanaClient:
    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        timeout: float = 30.0,
        proxy: str | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.auth = (username, password)
        self.timeout = timeout
        self.proxy = proxy

    def query_prometheus(
        self,
        expr: str,
        window: TimeWindow,
        instant: bool = True,
        datasource_uid: str = "prometheus",
    ) -> list[dict[str, Any]]:
        payload: dict[str, Any] = {
            "queries": [
                {
                    "refId": "A",
                    "datasource": {"type": "prometheus", "uid": datasource_uid},
                    "expr": expr,
                    "instant": instant,
                    "range": not instant,
                }
            ],
            "from": str(window.start_ms),
            "to": str(window.end_ms),
        }
        with httpx.Client(auth=self.auth, timeout=self.timeout, proxy=self.proxy) as client:
            resp = client.post(f"{self.base_url}/api/ds/query", json=payload)
            resp.raise_for_status()
            data = resp.json()
        frames: list[dict[str, Any]] = data.get("results", {}).get("A", {}).get("frames", [])
        return frames

    def query_mysql_scalar(
        self,
        raw_sql: str,
        datasource_uid: str,
        window: TimeWindow,
    ) -> int | None:
        payload: dict[str, Any] = {
            "queries": [
                {
                    "refId": "A",
                    "datasource": {"type": "mysql", "uid": datasource_uid},
                    "rawSql": raw_sql,
                    "format": "table",
                }
            ],
            "from": str(window.start_ms),
            "to": str(window.end_ms),
        }
        with httpx.Client(auth=self.auth, timeout=self.timeout, proxy=self.proxy) as client:
            resp = client.post(f"{self.base_url}/api/ds/query", json=payload)
            resp.raise_for_status()
            data = resp.json()

        frames: list[dict[str, Any]] = data.get("results", {}).get("A", {}).get("frames", [])
        for frame in frames:
            values = frame.get("data", {}).get("values", [])
            if values and values[0]:
                val = values[0][0]
                return int(val) if val is not None else None
        return None
