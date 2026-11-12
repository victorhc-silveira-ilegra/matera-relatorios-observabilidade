from __future__ import annotations

from typing import Any

import httpx

from app.domain.flagship.models import LogDistribution
from app.domain.time_window import TimeWindow

INDEX_PATTERN = "logs*"


def parse_log_distribution(data: dict[str, Any]) -> LogDistribution:
    buckets = data.get("aggregations", {}).get("levels", {}).get("buckets", [])
    counts: dict[str, int] = {}
    for bucket in buckets:
        key = str(bucket["key"]).upper()
        counts[key] = counts.get(key, 0) + int(bucket["doc_count"])
    return LogDistribution(total=sum(counts.values()), counts=counts)


class OpenSearchClient:
    def __init__(self, base_url: str, username: str, password: str, timeout: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.timeout = timeout

    def _login(self, client: httpx.Client) -> None:
        resp = client.post(
            f"{self.base_url}/_dashboards/auth/login",
            json={"username": self.username, "password": self.password},
            headers={"osd-xsrf": "true"},
        )
        resp.raise_for_status()

    def _search(self, client: httpx.Client, body: dict[str, Any]) -> dict[str, Any]:
        resp = client.post(
            f"{self.base_url}/_dashboards/api/console/proxy",
            params={"path": f"{INDEX_PATTERN}/_search", "method": "POST"},
            json=body,
            headers={"osd-xsrf": "true", "Content-Type": "application/json"},
        )
        resp.raise_for_status()
        payload: dict[str, Any] = resp.json()
        return payload

    @staticmethod
    def _time_range_filter(window: TimeWindow) -> dict[str, Any]:
        return {
            "range": {
                "@timestamp": {
                    "gte": window.start_utc_iso,
                    "lte": window.end_utc_iso,
                    "format": "strict_date_optional_time",
                }
            }
        }

    def fetch_log_distribution(
        self,
        window: TimeWindow,
        extra_filters: list[dict[str, Any]] | None = None,
    ) -> LogDistribution:
        must_filters: list[dict[str, Any]] = [self._time_range_filter(window)]
        if extra_filters:
            must_filters.extend(extra_filters)

        query_body: dict[str, Any] = {
            "size": 0,
            "track_total_hits": True,
            "query": {"bool": {"filter": must_filters}},
            "aggs": {"levels": {"terms": {"field": "level.keyword", "size": 10}}},
        }

        with httpx.Client(timeout=self.timeout) as client:
            self._login(client)
            data = self._search(client, query_body)
        return parse_log_distribution(data)

    def fetch_count(self, window: TimeWindow, filters: list[dict[str, Any]]) -> int:
        query_body: dict[str, Any] = {
            "size": 0,
            "track_total_hits": True,
            "query": {"bool": {"filter": [self._time_range_filter(window), *filters]}},
        }
        with httpx.Client(timeout=self.timeout) as client:
            self._login(client)
            data = self._search(client, query_body)
        return int(data.get("hits", {}).get("total", {}).get("value", 0))
