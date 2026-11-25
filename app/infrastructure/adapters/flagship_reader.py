from __future__ import annotations

import logging
from typing import Any

from app.domain.flagship.models import HmlMetrics, KafkaLag, LogDistribution, PodRestart, PrdMetrics
from app.domain.time_window import TimeWindow, WindowCount
from app.infrastructure.adapters.grafana import (
    GrafanaClient,
    extract_kafka_lags,
    extract_pod_restarts,
    extract_scalar_from_frames,
)
from app.infrastructure.adapters.opensearch import OpenSearchClient
from app.infrastructure.adapters.resilience import safe_collect
from app.infrastructure.settings import Settings


class FlagshipMetricsAdapter:
    def __init__(self, settings: Settings, logger: logging.Logger | None = None) -> None:
        self._logger = logger or logging.getLogger("relatorios")
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
        warnings: list[str] = []
        logs = safe_collect(
            "Logs HML",
            "Flagship",
            lambda: self._os_hml.fetch_log_distribution(window, extra_filters=None),
            LogDistribution(),
            warnings,
            self._logger,
        )
        incidents = safe_collect(
            "Incidentes HML",
            "Flagship",
            lambda: extract_scalar_from_frames(
                self._gf_hml.query_prometheus(
                    "sum by (topic) (increase(kafka_server_BrokerTopicMetrics_Count"
                    '{name="MessagesInPerSec", topic="hml.dtw.event.incident"}[30m]))',
                    window,
                    instant=True,
                )
            ),
            None,
            warnings,
            self._logger,
        )
        lags = safe_collect(
            "Lag HML",
            "Flagship",
            lambda: extract_kafka_lags(
                self._gf_hml.query_prometheus(
                    'kafka_consumer_group_ConsumerLagMetrics_Value{name="SumOffsetLag"} > 0 '
                    'unless (kafka_consumer_group_ConsumerLagMetrics_Value{name="SumOffsetLag", '
                    'groupId=~".*connect-teste-performance-bkp-12.*"} > 0 or '
                    'kafka_consumer_group_ConsumerLagMetrics_Value{name="SumOffsetLag", '
                    'groupId=~".*msk.canary.group.broker.*"} > 0)',
                    window,
                    instant=False,
                )
            ),
            list[KafkaLag](),
            warnings,
            self._logger,
        )
        restarts = safe_collect(
            "Restarts HML",
            "Flagship",
            lambda: extract_pod_restarts(
                self._gf_hml.query_prometheus(
                    'increase(kube_pod_container_status_restarts_total{namespace="dtw-hml"}'
                    f"[{window.duration_promql}]) "
                    'and kube_pod_container_status_running{namespace="dtw-hml"} > 0',
                    window,
                    instant=False,
                )
            ),
            list[PodRestart](),
            warnings,
            self._logger,
        )
        return HmlMetrics(logs=logs, incidents=incidents, lags=lags, restarts=restarts, warnings=warnings)

    def _safe_os_count(self, scope: str, window: TimeWindow, filters: list[dict[str, Any]], warnings: list[str]) -> int:
        return safe_collect(
            scope,
            "Flagship",
            lambda: self._os_prd.fetch_count(window, filters),
            0,
            warnings,
            self._logger,
        )

    def read_prd(self, current_window: TimeWindow, day_windows: list[TimeWindow]) -> PrdMetrics:
        warnings: list[str] = []
        logs = safe_collect(
            "Logs PRD",
            "Flagship",
            lambda: self._os_prd.fetch_log_distribution(current_window, extra_filters=None),
            LogDistribution(),
            warnings,
            self._logger,
        )

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
        routing_errors = [
            WindowCount(w.label, self._safe_os_count("Logs de Erro PRD", w, routing_filters, warnings))
            for w in day_windows
        ]

        api_filters = [
            {"match_phrase": {"kubernetes.container_name.keyword": "dtw-transaction-api"}},
            {
                "match_phrase": {
                    "message": ("Check the difference between the delta and physical balance table on account")
                }
            },
            {"match_phrase": {"level": "ERROR"}},
        ]
        api_hits = [
            WindowCount(w.label, self._safe_os_count("API Hits PRD", w, api_filters, warnings)) for w in day_windows
        ]

        incidents = safe_collect(
            "Incidentes PRD",
            "Flagship",
            lambda: extract_scalar_from_frames(
                self._gf_prd.query_prometheus(
                    "sum by (topic) (increase(kafka_server_BrokerTopicMetrics_Count"
                    '{name="MessagesInPerSec", topic="prod.dtw.event.incident"}[30m]))',
                    current_window,
                    instant=True,
                )
            ),
            None,
            warnings,
            self._logger,
        )
        lags = safe_collect(
            "Lag PRD",
            "Flagship",
            lambda: extract_kafka_lags(
                self._gf_prd.query_prometheus(
                    'kafka_consumer_group_ConsumerLagMetrics_Value{name="SumOffsetLag"} > 0 '
                    'unless (kafka_consumer_group_ConsumerLagMetrics_Value{name="SumOffsetLag", '
                    'groupId=~".*dtw-msk-prod-backup.*"} > 0 or '
                    'kafka_consumer_group_ConsumerLagMetrics_Value{name="SumOffsetLag", '
                    'groupId=~".*msk.canary.group.broker.*"} > 0)',
                    current_window,
                    instant=False,
                )
            ),
            list[KafkaLag](),
            warnings,
            self._logger,
        )
        restarts = safe_collect(
            "Restarts PRD",
            "Flagship",
            lambda: extract_pod_restarts(
                self._gf_prd.query_prometheus(
                    'increase(kube_pod_container_status_restarts_total{namespace="dtw-prod"}'
                    f"[{current_window.duration_promql}]) "
                    'and kube_pod_container_status_running{namespace="dtw-prod"} > 0',
                    current_window,
                    instant=False,
                )
            ),
            list[PodRestart](),
            warnings,
            self._logger,
        )
        saga_total = safe_collect(
            "Integração SAGA",
            "Flagship",
            lambda: self._gf_prd.query_mysql_scalar(
                "select count(*) from STDIN_CONTROLE_SAGA_INTEGRACAO where integrated = 'N'",
                datasource_uid="4hs8MXdIz",
                window=current_window,
            ),
            None,
            warnings,
            self._logger,
        )
        saga_above_5m = safe_collect(
            "Integração SAGA (>5m)",
            "Flagship",
            lambda: self._gf_prd.query_mysql_scalar(
                "SELECT COUNT(*) AS quantidade_registros "
                "FROM STDIN_CONTROLE_SAGA_INTEGRACAO "
                "WHERE integrated = 'N' "
                "AND DATE_ADD(created, INTERVAL 3 HOUR) <= NOW() - INTERVAL 5 MINUTE;",
                datasource_uid="4hs8MXdIz",
                window=current_window,
            ),
            None,
            warnings,
            self._logger,
        )
        polling_processed = safe_collect(
            "Polling DTW_TR_POLLING_ENTRY",
            "Flagship",
            lambda: self._gf_prd.query_mysql_scalar(
                "SELECT COUNT(*) FROM DTW_TR_POLLING_ENTRY WHERE PROCESSED IN (0,1);",
                datasource_uid="T2rqmE8Sk",
                window=current_window,
            ),
            None,
            warnings,
            self._logger,
        )
        polling_total = safe_collect(
            "Polling DTW_TR_POLLING_ENTRY (pendentes)",
            "Flagship",
            lambda: self._gf_prd.query_mysql_scalar(
                "SELECT COUNT(0) FROM DTW_TR_POLLING_ENTRY WHERE PROCESSED = 0;",
                datasource_uid="T2rqmE8Sk",
                window=current_window,
            ),
            None,
            warnings,
            self._logger,
        )
        polling_partitions = safe_collect(
            "Polling DTW_TR_POLLING_ENTRY (partições)",
            "Flagship",
            lambda: self._gf_prd.query_mysql_column(
                "SELECT PARTITION_NUMBER FROM DTW_TR_POLLING_ENTRY WHERE PROCESSED = 0 GROUP BY PARTITION_NUMBER;",
                datasource_uid="T2rqmE8Sk",
                window=current_window,
            ),
            list[int](),
            warnings,
            self._logger,
        )

        return PrdMetrics(
            logs=logs,
            routing_errors_by_window=routing_errors,
            incidents=incidents,
            lags=lags,
            restarts=restarts,
            saga_total=saga_total,
            saga_above_5m=saga_above_5m,
            polling_processed=polling_processed,
            polling_total=polling_total,
            polling_partitions=polling_partitions,
            api_hits_by_window=api_hits,
            warnings=warnings,
        )
