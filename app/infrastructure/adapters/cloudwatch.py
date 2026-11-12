from __future__ import annotations

import json
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from playwright.sync_api import Response, sync_playwright

from app.domain.flagship.models import RdsInstanceCpu, RdsMetrics
from app.domain.time_window import TimeWindow

RDS_DISPLAY_NAMES: dict[str, str] = {
    "dtw-prod-cluster-transaction-1": "transaction-1",
    "dtw-prod-cluster-conciliation-1": "conciliation-1",
    "dtw-prod-cluster-entrypoints-1": "entrypoints-1",
    "dtw-prod-cluster-compositetransaction-1": "compositetransaction-1",
    "dtw-prod-cluster-balancestatement-1": "balancestatement-1",
    "matinc-si-prd-database": "matinc-si-prd-database",
    "dtw-prod-cluster-keycloak-1": "keycloak-1",
}


def build_windowed_url(base_url: str, window: TimeWindow) -> str:
    parsed = urlparse(base_url)
    qs = parse_qs(parsed.query)
    qs["start"] = [window.start_utc_iso]
    qs["end"] = [window.end_utc_iso]
    new_query = urlencode(qs, doseq=True)
    return urlunparse(parsed._replace(query=new_query))


def parse_rds_metric_data(payload: dict[str, Any]) -> RdsMetrics:
    metric_data = payload.get("MetricData", [])
    instances: list[RdsInstanceCpu] = []
    peaks_above_90: list[RdsInstanceCpu] = []

    for series in metric_data:
        raw_label = str(series.get("Label", ""))
        if raw_label not in RDS_DISPLAY_NAMES:
            continue
        display_name = RDS_DISPLAY_NAMES[raw_label]
        values = [float(v) for v in series.get("Values", []) if v is not None]
        if not values:
            instances.append(RdsInstanceCpu(name=display_name, current_pct=None, peak_pct=None))
            continue

        timestamps = series.get("Timestamps", [])
        current_val = values[-1] if len(timestamps) >= 2 and timestamps[0] < timestamps[-1] else values[0]

        peak_val = max(values)
        points_above_90 = sum(1 for v in values if v >= 90.0)
        inst = RdsInstanceCpu(
            name=display_name,
            current_pct=round(current_val, 3),
            peak_pct=round(peak_val, 3),
            points_above_90=points_above_90,
        )
        instances.append(inst)
        if peak_val >= 90.0:
            peaks_above_90.append(inst)

    instances.sort(key=lambda i: i.current_pct if i.current_pct is not None else -1.0, reverse=True)
    peaks_above_90.sort(key=lambda i: i.peak_pct if i.peak_pct is not None else -1.0, reverse=True)
    return RdsMetrics(peaks_above_90=peaks_above_90, instances=instances)


class CloudWatchRdsAdapter:
    def __init__(self, dashboard_url: str, timeout_ms: int = 45000) -> None:
        self._dashboard_url = dashboard_url
        self._timeout_ms = timeout_ms

    def read_rds_cpu(self, window: TimeWindow) -> RdsMetrics:
        target_url = build_windowed_url(self._dashboard_url, window)
        captured_payload: dict[str, Any] | None = None

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                page = browser.new_page()

                def on_response(resp: Response) -> None:
                    nonlocal captured_payload
                    if captured_payload is not None:
                        return
                    if "monitoring." in resp.url and resp.request.method == "POST" and resp.status == 200:
                        try:
                            text = resp.text()
                            if "dtw-prod-cluster-transaction-1" in text and "MetricData" in text:
                                captured_payload = json.loads(text)
                        except Exception:
                            return

                page.on("response", on_response)
                page.goto(target_url, wait_until="networkidle", timeout=self._timeout_ms)
                if captured_payload is None:
                    page.wait_for_timeout(4000)
            finally:
                browser.close()

        if captured_payload is None:
            return RdsMetrics(error="Nao foi possivel capturar os dados do widget RDS CPU no CloudWatch.")
        return parse_rds_metric_data(captured_payload)
