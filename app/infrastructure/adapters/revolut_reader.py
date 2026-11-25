from __future__ import annotations

import logging
from typing import Any

from app.domain.revolut.formatter import evaluate_revolut_status
from app.domain.revolut.models import (
    RevolutHttpError,
    RevolutLatency,
    RevolutPodRestart,
    RevolutReportData,
    RevolutServiceError,
    RevolutWindowStatus,
)
from app.domain.time_window import TimeWindow, WindowCount
from app.infrastructure.adapters.grafana import (
    GrafanaClient,
    clean_float,
    extract_pod_restarts,
    extract_scalar_from_frames,
)
from app.infrastructure.adapters.resilience import safe_collect
from app.infrastructure.settings import Settings

NAMESPACE = "mip-prd"

SPI_SERVICES: list[str] = [
    "spi-addressing",
    "spi-addressing-jobs",
    "spi-addressing-queues",
    "spi-auto-pix-messenger",
    "spi-dispute",
    "spi-main",
    "spi-messaging",
    "spi-messaging-processor",
    "spi-messaging-secondary",
    "spi-messaging-secondary-processor",
    "spi-qrcodes1",
    "spi-qrcodes2",
]

LOG_SPIKE_TRIGGER_THRESHOLD = 50.0
LOG_M5_NORMALIZED_MAX = 100.0
LOG_CURR_NORMALIZED_MAX = 25.0


def extract_label_map(frames: list[dict[str, Any]], label_key: str) -> dict[str, float]:
    result: dict[str, float] = {}
    for frame in frames:
        fields = frame.get("schema", {}).get("fields", [])
        values = frame.get("data", {}).get("values", [])
        if len(fields) < 2 or len(values) < 2 or not values[1]:
            continue
        labels = fields[1].get("labels", {})
        key_val = labels.get(label_key)
        if not key_val:
            continue
        non_null = [float(v) for v in values[1] if v is not None]
        if non_null:
            result[str(key_val)] = result.get(str(key_val), 0.0) + non_null[-1]
    return result


def extract_services_map(frames: list[dict[str, Any]]) -> dict[str, float]:
    return extract_label_map(frames, "service")


class RevolutMetricsAdapter:
    def __init__(self, settings: Settings, logger: logging.Logger | None = None) -> None:
        if not settings.grafana_revolut_user or not settings.grafana_revolut_pass:
            raise ValueError("Credenciais GRAFANA_REVOLUT_USER/GRAFANA_REVOLUT_PASS nao configuradas no .env")
        self._logger = logger or logging.getLogger("relatorios")
        self._gf = GrafanaClient(
            base_url=settings.grafana_revolut_base,
            username=settings.grafana_revolut_user,
            password=settings.grafana_revolut_pass,
            proxy=settings.revolut_http_proxy or None,
        )

    def _query_scalar(self, expr: str, window: TimeWindow) -> float | None:
        return clean_float(extract_scalar_from_frames(self._gf.query_prometheus(expr, window, instant=True)))

    def _safe_scalar(self, scope: str, expr: str, window: TimeWindow, warnings: list[str]) -> float | None:
        return safe_collect(scope, "Revolut", lambda: self._query_scalar(expr, window), None, warnings, self._logger)

    def _safe_prom(
        self, scope: str, expr: str, window: TimeWindow, warnings: list[str], *, instant: bool = True
    ) -> list[dict[str, Any]]:
        return safe_collect(
            scope,
            "Revolut",
            lambda: self._gf.query_prometheus(expr, window, instant=instant),
            [],
            warnings,
            self._logger,
        )

    def _collect_window_metrics(
        self,
        window: TimeWindow,
        warnings: list[str],
    ) -> tuple[
        RevolutLatency,
        RevolutLatency,
        list[RevolutServiceError],
        list[RevolutServiceError],
        list[RevolutPodRestart],
        list[RevolutHttpError],
    ]:
        dur = window.duration_promql

        pag_b = f'payment_execution_seconds_bucket{{service="spi-main",namespace="{NAMESPACE}"}}[{dur}]'
        rec_b = f'credit_validation_seconds_bucket{{eventType="receipt",namespace="{NAMESPACE}"}}[{dur}]'
        pagador_p50 = self._safe_scalar(
            "Latência Pagador", f"histogram_quantile(0.5, sum by (le) (rate({pag_b})))", window, warnings
        )
        pagador_p95 = self._safe_scalar(
            "Latência Pagador", f"histogram_quantile(0.95, sum by (le) (rate({pag_b})))", window, warnings
        )
        recebedor_p50 = self._safe_scalar(
            "Latência Recebedor", f"histogram_quantile(0.5, sum by (le) (rate({rec_b})))", window, warnings
        )
        recebedor_p95 = self._safe_scalar(
            "Latência Recebedor", f"histogram_quantile(0.95, sum by (le) (rate({rec_b})))", window, warnings
        )

        err_frames = self._safe_prom(
            "Logs SPI",
            f'sum by (service) (increase(logback_events_total{{namespace="{NAMESPACE}", level="error"}}[15m]))',
            window,
            warnings,
        )
        svc_map = extract_services_map(err_frames)
        has_alert = any(val >= LOG_SPIKE_TRIGGER_THRESHOLD for val in svc_map.values())

        svc_map_m5: dict[str, float] = {}
        svc_map_curr: dict[str, float] = {}

        if has_alert:
            f_m5 = self._safe_prom(
                "Logs SPI",
                f'sum by (service) (increase(logback_events_total{{namespace="{NAMESPACE}", level="error"}}[5m]))',
                window,
                warnings,
            )
            f_curr = self._safe_prom(
                "Logs SPI",
                f'sum by (service) (increase(logback_events_total{{namespace="{NAMESPACE}", level="error"}}[1m]))',
                window,
                warnings,
            )
            svc_map_m5 = extract_services_map(f_m5)
            svc_map_curr = extract_services_map(f_curr)

        with_errors: list[RevolutServiceError] = []
        without_errors: list[RevolutServiceError] = []
        for svc in SPI_SERVICES:
            val = svc_map.get(svc, 0.0)
            if val >= LOG_SPIKE_TRIGGER_THRESHOLD:
                v_m5 = svc_map_m5.get(svc, 0.0)
                v_curr = svc_map_curr.get(svc, 0.0)
                is_normalized = (v_m5 < LOG_M5_NORMALIZED_MAX) and (v_curr < LOG_CURR_NORMALIZED_MAX)
                if is_normalized:
                    without_errors.append(RevolutServiceError(service=svc, value=v_curr))
                else:
                    with_errors.append(RevolutServiceError(service=svc, value=val))
            else:
                without_errors.append(RevolutServiceError(service=svc, value=val))

        raw_restarts = extract_pod_restarts(
            self._safe_prom(
                "Restarts",
                f'increase(kube_pod_container_status_restarts_total{{namespace="{NAMESPACE}"}}[{dur}]) '
                f'and kube_pod_container_status_running{{namespace="{NAMESPACE}"}} > 0',
                window,
                warnings,
                instant=False,
            )
        )
        restarts = [RevolutPodRestart(pod=r.pod, restarts=r.restarts) for r in raw_restarts]

        raw_5xx = extract_label_map(
            self._safe_prom(
                "HTTP 5XX",
                "sum by (job) (increase(http_server_requests_seconds_count"
                f'{{namespace="{NAMESPACE}",status=~"5.."}}[{dur}])) > 0',
                window,
                warnings,
            ),
            label_key="job",
        )
        http_5xx = [
            RevolutHttpError(service=svc, count=int(round(cnt)))
            for svc, cnt in sorted(raw_5xx.items(), key=lambda kv: kv[1], reverse=True)
            if int(round(cnt)) > 0
        ]

        return (
            RevolutLatency(p50_seconds=pagador_p50, p95_seconds=pagador_p95),
            RevolutLatency(p50_seconds=recebedor_p50, p95_seconds=recebedor_p95),
            with_errors,
            without_errors,
            restarts,
            http_5xx,
        )

    def read_revolut(
        self,
        current_window: TimeWindow,
        day_windows: list[TimeWindow],
        responsavel: str,
        chamados: str,
    ) -> RevolutReportData:
        has_ticket = chamados.strip().lower().rstrip(".") not in {"sem ocorrências", "sem ocorrencias", ""}
        recebedor_pix: list[WindowCount] = []
        pagador_pix: list[WindowCount] = []
        window_statuses: list[RevolutWindowStatus] = []

        current_pag_latency = RevolutLatency()
        current_rec_latency = RevolutLatency()
        current_with_errors: list[RevolutServiceError] = []
        current_without_errors: list[RevolutServiceError] = []
        current_restarts: list[RevolutPodRestart] = []
        current_http_5xx: list[RevolutHttpError] = []

        warnings: list[str] = []
        for w in day_windows:
            w_dur = w.duration_promql
            rec_val = self._safe_scalar(
                "PIXs Recebedor",
                f'sum(increase(incoming_messages_item_seconds_count{{eventType="receipt",messageType="pacs.008",namespace="{NAMESPACE}"}}[{w_dur}]))',
                w,
                warnings,
            )
            pag_val = self._safe_scalar(
                "PIXs Pagador",
                f'sum(increase(payment_execution_seconds_count{{service="spi-main",namespace="{NAMESPACE}"}}[{w_dur}]))',
                w,
                warnings,
            )
            w_label = f"{w.start_brt.strftime('%H:%M')} à {w.end_brt.strftime('%H:%M')}"
            recebedor_pix.append(WindowCount(w_label, int(round(rec_val or 0))))
            pagador_pix.append(WindowCount(w_label, int(round(pag_val or 0))))

            pag_lat, rec_lat, w_with_err, w_without_err, w_restarts, w_5xx = self._collect_window_metrics(w, warnings)
            w_period_label = f"{w.start_brt.strftime('%H:%M')}h - {w.end_brt.strftime('%H:%M')}h"
            eval_res = evaluate_revolut_status(
                pagador_latency=pag_lat,
                recebedor_latency=rec_lat,
                err_count=len(w_with_err),
                total_services=len(w_with_err) + len(w_without_err),
                has_ticket=has_ticket if w.key == current_window.key else False,
                services_with_errors=tuple(w_with_err),
                restarts=tuple(w_restarts),
                http_5xx_errors=tuple(w_5xx),
            )
            window_statuses.append(
                RevolutWindowStatus(
                    period_label=w_period_label,
                    badge=eval_res.badge,
                    critical_events=eval_res.critical_events,
                    critical_event_details=eval_res.critical_details,
                )
            )
            if w.key == current_window.key:
                current_pag_latency = pag_lat
                current_rec_latency = rec_lat
                current_with_errors = w_with_err
                current_without_errors = w_without_err
                current_restarts = w_restarts
                current_http_5xx = w_5xx

        date_full = current_window.end_brt.strftime("%d/%m/%Y")
        end_hhmm = current_window.end_brt.strftime("%H:%M")
        next_label = {
            "10:30": f"{date_full} às 13:30h",
            "13:30": f"{date_full} às 16:30h",
        }.get(end_hhmm, "próximo dia útil às 10:30h")

        return RevolutReportData(
            date_full=date_full,
            period_label=f"{current_window.start_brt.strftime('%H:%M')}h - {current_window.end_brt.strftime('%H:%M')}h",
            current_window_label=current_window.label,
            responsavel=responsavel,
            pagador_latency=current_pag_latency,
            recebedor_latency=current_rec_latency,
            recebedor_pix_by_window=recebedor_pix,
            pagador_pix_by_window=pagador_pix,
            services_with_errors=current_with_errors,
            services_without_errors=current_without_errors,
            restarts=current_restarts,
            http_5xx_errors=current_http_5xx,
            window_statuses=window_statuses,
            chamados=chamados,
            next_analysis_label=next_label,
            collection_warnings=warnings,
        )
