from __future__ import annotations

from typing import Any

from app.domain.revolut.models import (
    RevolutLatency,
    RevolutReportData,
    RevolutServiceError,
)
from app.domain.time_window import TimeWindow, WindowCount
from app.infrastructure.adapters.grafana import (
    GrafanaClient,
    clean_float,
    extract_scalar_from_frames,
)
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


def extract_services_map(frames: list[dict[str, Any]]) -> dict[str, float]:
    result: dict[str, float] = {}
    for frame in frames:
        fields = frame.get("schema", {}).get("fields", [])
        values = frame.get("data", {}).get("values", [])
        if len(fields) < 2 or len(values) < 2 or not values[1]:
            continue
        labels = fields[1].get("labels", {})
        svc = labels.get("service")
        if not svc:
            continue
        non_null = [float(v) for v in values[1] if v is not None]
        if non_null:
            result[str(svc)] = non_null[-1]
    return result


class RevolutMetricsAdapter:
    def __init__(self, settings: Settings) -> None:
        if not settings.grafana_revolut_user or not settings.grafana_revolut_pass:
            raise ValueError("Credenciais GRAFANA_REVOLUT_USER/GRAFANA_REVOLUT_PASS nao configuradas no .env")
        self._gf = GrafanaClient(
            base_url=settings.grafana_revolut_base,
            username=settings.grafana_revolut_user,
            password=settings.grafana_revolut_pass,
            proxy=settings.revolut_http_proxy or None,
        )

    def read_revolut(
        self,
        current_window: TimeWindow,
        day_windows: list[TimeWindow],
        responsavel: str,
        chamados: str,
    ) -> RevolutReportData:
        dur = current_window.duration_promql

        pagador_p50 = clean_float(
            extract_scalar_from_frames(
                self._gf.query_prometheus(
                    "histogram_quantile(0.5, sum by (le) (rate(payment_execution_seconds_bucket"
                    f'{{service="spi-main",namespace="{NAMESPACE}"}}[{dur}])))',
                    current_window,
                    instant=True,
                )
            )
        )
        pagador_p95 = clean_float(
            extract_scalar_from_frames(
                self._gf.query_prometheus(
                    "histogram_quantile(0.95, sum by (le) (rate(payment_execution_seconds_bucket"
                    f'{{service="spi-main",namespace="{NAMESPACE}"}}[{dur}])))',
                    current_window,
                    instant=True,
                )
            )
        )
        recebedor_p50 = clean_float(
            extract_scalar_from_frames(
                self._gf.query_prometheus(
                    "histogram_quantile(0.5, sum by (le) (rate(credit_validation_seconds_bucket"
                    f'{{eventType="receipt",namespace="{NAMESPACE}"}}[{dur}])))',
                    current_window,
                    instant=True,
                )
            )
        )
        recebedor_p95 = clean_float(
            extract_scalar_from_frames(
                self._gf.query_prometheus(
                    "histogram_quantile(0.95, sum by (le) (rate(credit_validation_seconds_bucket"
                    f'{{eventType="receipt",namespace="{NAMESPACE}"}}[{dur}])))',
                    current_window,
                    instant=True,
                )
            )
        )

        recebedor_pix: list[WindowCount] = []
        pagador_pix: list[WindowCount] = []
        for w in day_windows:
            w_dur = w.duration_promql
            rec_val = clean_float(
                extract_scalar_from_frames(
                    self._gf.query_prometheus(
                        f'sum(increase(incoming_messages_item_seconds_count{{eventType="receipt",messageType="pacs.008",namespace="{NAMESPACE}"}}[{w_dur}]))',
                        w,
                        instant=True,
                    )
                )
            )
            pag_val = clean_float(
                extract_scalar_from_frames(
                    self._gf.query_prometheus(
                        f'sum(increase(payment_execution_seconds_count{{service="spi-main",namespace="{NAMESPACE}"}}[{w_dur}]))',
                        w,
                        instant=True,
                    )
                )
            )
            w_label = f"{w.start_brt.strftime('%H:%M')} à {w.end_brt.strftime('%H:%M')}"
            recebedor_pix.append(WindowCount(w_label, int(round(rec_val or 0))))
            pagador_pix.append(WindowCount(w_label, int(round(pag_val or 0))))

        err_frames = self._gf.query_prometheus(
            f'sum by (service) (increase(logback_events_total{{namespace="{NAMESPACE}", level="error"}}[15m]))',
            current_window,
            instant=True,
        )
        svc_map = extract_services_map(err_frames)
        has_alert = any(val >= LOG_SPIKE_TRIGGER_THRESHOLD for val in svc_map.values())

        svc_map_m5: dict[str, float] = {}
        svc_map_curr: dict[str, float] = {}

        if has_alert:
            f_m5 = self._gf.query_prometheus(
                f'sum by (service) (increase(logback_events_total{{namespace="{NAMESPACE}", level="error"}}[5m]))',
                current_window,
                instant=True,
            )
            f_curr = self._gf.query_prometheus(
                f'sum by (service) (increase(logback_events_total{{namespace="{NAMESPACE}", level="error"}}[1m]))',
                current_window,
                instant=True,
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

        date_full = current_window.end_brt.strftime("%d/%m/%Y")
        end_hhmm = current_window.end_brt.strftime("%H:%M")
        if end_hhmm == "10:30":
            next_label = f"{date_full} às 13:30h"
        elif end_hhmm == "13:30":
            next_label = f"{date_full} às 16:30h"
        else:
            next_label = "próximo dia útil às 10:30h"

        return RevolutReportData(
            date_full=date_full,
            period_label=f"{current_window.start_brt.strftime('%H:%M')}h - {current_window.end_brt.strftime('%H:%M')}h",
            current_window_label=current_window.label,
            responsavel=responsavel,
            pagador_latency=RevolutLatency(p50_seconds=pagador_p50, p95_seconds=pagador_p95),
            recebedor_latency=RevolutLatency(p50_seconds=recebedor_p50, p95_seconds=recebedor_p95),
            recebedor_pix_by_window=recebedor_pix,
            pagador_pix_by_window=pagador_pix,
            services_with_errors=with_errors,
            services_without_errors=without_errors,
            chamados=chamados,
            next_analysis_label=next_label,
        )
