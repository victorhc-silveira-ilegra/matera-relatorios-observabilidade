from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from app.domain.flagship.models import HmlMetrics, PrdMetrics
from app.domain.time_window import TimeWindow, WindowCount
from app.infrastructure.adapters.grafana import (
    GrafanaClient,
    extract_pod_restarts,
    extract_scalar_from_frames,
)
from app.infrastructure.adapters.opensearch import OpenSearchClient
from app.infrastructure.settings import Settings


class FlagshipMetricsAdapter:
    def __init__(self, settings: Settings) -> None:
        self._os_hml = OpenSearchClient(
            base_url=settings.opensearch_hml_base,
            username=settings.kibana_hml_user,
            password=settings.kibana_hml_pass,
        )
        self._os_prd = OpenSearchClient(
            base_url=settings.opensearch_prd_base,
            username=settings.kibana_prd_user,
            password=settings.kibana_prd_pass,
        )
        self._gf_hml = GrafanaClient(
            base_url=settings.grafana_hml_base,
            username=settings.grafana_user,
            password=settings.grafana_pass,
        )
        self._gf_prd = GrafanaClient(
            base_url=settings.grafana_prd_base,
            username=settings.grafana_user,
            password=settings.grafana_pass,
        )

    def read_hml(self, window: TimeWindow) -> HmlMetrics:
        now_brt = datetime.now(ZoneInfo("America/Sao_Paulo"))
        incident_window = TimeWindow("realtime", now_brt, now_brt) if now_brt > window.end_brt else window
        logs = self._os_hml.fetch_log_distribution(window, extra_filters=None)
        incidents = extract_scalar_from_frames(
            self._gf_hml.query_prometheus(
                "sum by (topic) (increase(kafka_server_BrokerTopicMetrics_Count"
                '{name="MessagesInPerSec", topic="hml.dtw.event.incident"}[5h]))',
                incident_window,
                instant=True,
            )
        )
        lag = extract_scalar_from_frames(
            self._gf_hml.query_prometheus(
                'kafka_consumer_group_ConsumerLagMetrics_Value{name="SumOffsetLag"} > 0 '
                'unless (kafka_consumer_group_ConsumerLagMetrics_Value{name="SumOffsetLag", '
                'groupId=~".*connect-teste-performance-bkp-12.*"} > 0 or '
                'kafka_consumer_group_ConsumerLagMetrics_Value{name="SumOffsetLag", '
                'groupId=~".*msk.canary.group.broker.*"} > 0)',
                window,
                instant=True,
            )
        )
        restarts = extract_pod_restarts(
            self._gf_hml.query_prometheus(
                'increase(kube_pod_container_status_restarts_total{namespace="dtw-hml"}[6h])',
                window,
                instant=True,
            )
        )
        return HmlMetrics(logs=logs, incidents=incidents, lag=lag, restarts=restarts)

    def read_prd(self, current_window: TimeWindow, day_windows: list[TimeWindow]) -> PrdMetrics:
        logs = self._os_prd.fetch_log_distribution(current_window, extra_filters=None)

        routing_filters = [
            {
                "match_phrase": {
                    "kubernetes.labels.app_kubernetes_io/application.keyword": (
                        "cc-integration-event-routing-entry-producer"
                    )
                }
            },
            {"match_phrase": {"level.keyword": "ERROR"}},
        ]
        routing_errors = [WindowCount(w.label, self._os_prd.fetch_count(w, routing_filters)) for w in day_windows]

        api_filters = [
            {"match_phrase": {"kubernetes.container_name.keyword": "dtw-transaction-api"}},
            {
                "match_phrase": {
                    "message": ("Check the difference between the delta and physical balance table on account")
                }
            },
            {"match_phrase": {"level": "ERROR"}},
        ]
        api_hits = [WindowCount(w.label, self._os_prd.fetch_count(w, api_filters)) for w in day_windows]

        now_brt = datetime.now(ZoneInfo("America/Sao_Paulo"))
        incident_window = (
            TimeWindow("realtime", now_brt, now_brt) if now_brt > current_window.end_brt else current_window
        )
        incidents = extract_scalar_from_frames(
            self._gf_prd.query_prometheus(
                "sum by (topic) (increase(kafka_server_BrokerTopicMetrics_Count"
                '{name="MessagesInPerSec", topic="prod.dtw.event.incident"}[30m]))',
                incident_window,
                instant=True,
            )
        )
        lag = extract_scalar_from_frames(
            self._gf_prd.query_prometheus(
                'kafka_consumer_group_ConsumerLagMetrics_Value{name="SumOffsetLag"} > 0 '
                'unless (kafka_consumer_group_ConsumerLagMetrics_Value{name="SumOffsetLag", '
                'groupId=~".*dtw-msk-prod-backup.*"} > 0 or '
                'kafka_consumer_group_ConsumerLagMetrics_Value{name="SumOffsetLag", '
                'groupId=~".*msk.canary.group.broker.*"} > 0)',
                current_window,
                instant=True,
            )
        )
        restarts = extract_pod_restarts(
            self._gf_prd.query_prometheus(
                'increase(kube_pod_container_status_restarts_total{namespace="dtw-prod"}[1m])',
                current_window,
                instant=True,
            )
        )
        saga_total = self._gf_prd.query_mysql_scalar(
            "select count(*) from STDIN_CONTROLE_SAGA_INTEGRACAO where integrated = 'N'",
            datasource_uid="4hs8MXdIz",
            window=current_window,
        )
        saga_above_5m = self._gf_prd.query_mysql_scalar(
            "SELECT COUNT(*) AS quantidade_registros "
            "FROM STDIN_CONTROLE_SAGA_INTEGRACAO "
            "WHERE integrated = 'N' "
            "AND DATE_ADD(created, INTERVAL 3 HOUR) <= NOW() - INTERVAL 5 MINUTE;",
            datasource_uid="4hs8MXdIz",
            window=current_window,
        )
        polling_processed = self._gf_prd.query_mysql_scalar(
            "SELECT COUNT(*) FROM DTW_TR_POLLING_ENTRY WHERE PROCESSED IN (0,1);",
            datasource_uid="T2rqmE8Sk",
            window=current_window,
        )
        polling_total = self._gf_prd.query_mysql_scalar(
            "SELECT COUNT(0) FROM DTW_TR_POLLING_ENTRY WHERE PROCESSED = 0;",
            datasource_uid="T2rqmE8Sk",
            window=current_window,
        )

        return PrdMetrics(
            logs=logs,
            routing_errors_by_window=routing_errors,
            incidents=incidents,
            lag=lag,
            restarts=restarts,
            saga_total=saga_total,
            saga_above_5m=saga_above_5m,
            polling_processed=polling_processed,
            polling_total=polling_total,
            api_hits_by_window=api_hits,
        )
