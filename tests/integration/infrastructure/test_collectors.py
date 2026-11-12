import math
from typing import Any

from app.domain.flagship.models import LogDistribution
from app.infrastructure.adapters.cloudwatch import build_windowed_url, parse_rds_metric_data
from app.infrastructure.adapters.grafana import (
    clean_float,
    extract_pod_restarts,
    extract_scalar_from_frames,
)
from app.infrastructure.adapters.opensearch import parse_log_distribution
from app.infrastructure.adapters.revolut_reader import extract_services_map


def test_clean_float() -> None:
    assert clean_float(None) is None
    assert clean_float(math.nan) is None
    assert clean_float(math.inf) is None
    assert clean_float(1.5) == 1.5


def test_log_distribution_zero_total() -> None:
    dist = LogDistribution(total=0, counts={})
    assert dist.pct("INFO") == 0.0
    assert dist.count("INFO") == 0


def test_extract_scalar_from_frames() -> None:
    assert extract_scalar_from_frames([{"data": {"values": [[1], [14.2]]}}]) == 14.2
    assert extract_scalar_from_frames([{"data": {"values": [[1], [None]]}}]) is None
    assert extract_scalar_from_frames([{"data": {"values": []}}]) is None
    assert extract_scalar_from_frames([]) is None


def test_extract_pod_restarts() -> None:
    frames: list[dict[str, Any]] = [
        {
            "schema": {"fields": [{"name": "Time"}, {"name": "Value", "labels": {"pod": "pod-a"}}]},
            "data": {"values": [[1], [2.96]]},
        },
        {
            "schema": {"fields": [{"name": "Time"}, {"name": "Value", "labels": {"pod": "pod-b"}}]},
            "data": {"values": [[1], [0.0]]},
        },
        {"schema": {"fields": [{"name": "Time"}]}, "data": {"values": [[1]]}},
    ]
    restarts = extract_pod_restarts(frames)
    assert len(restarts) == 1
    assert restarts[0].pod == "pod-a"
    assert restarts[0].restarts == 2.96


def test_parse_rds_metric_data() -> None:
    payload = {
        "MetricData": [
            {
                "Label": "dtw-prod-cluster-transaction-1",
                "Timestamps": [1794493500.0, 1794493200.0],
                "Values": [44.7031, 91.5],
            },
            {
                "Label": "dtw-prod-cluster-conciliation-1",
                "Timestamps": [1794493200.0, 1794493500.0],
                "Values": [30.0, 25.685],
            },
            {
                "Label": "dtw-prod-cluster-entrypoints-1",
                "Timestamps": [],
                "Values": [],
            },
            {
                "Label": "unrelated-series",
                "Timestamps": [1794493500.0],
                "Values": [99.0],
            },
        ]
    }
    rds = parse_rds_metric_data(payload)
    assert [i.name for i in rds.instances] == [
        "transaction-1",
        "conciliation-1",
        "entrypoints-1",
    ]
    assert rds.instances[0].current_pct == 44.703
    assert rds.instances[1].current_pct == 25.685
    assert rds.instances[2].current_pct is None
    assert len(rds.peaks_above_90) == 1
    assert rds.peaks_above_90[0].points_above_90 == 1


def test_build_windowed_url() -> None:
    from datetime import date

    from app.domain.time_window import build_time_window

    w = build_time_window(date(2026, 11, 12), "08:30-10:30")
    url = build_windowed_url("https://cloudwatch.amazonaws.com/dashboard.html?start=PT3H&end=null", w)
    assert "2026-11-12T11%3A30%3A00.000Z" in url


def test_parse_log_distribution_case_insensitive() -> None:
    payload = {
        "aggregations": {
            "levels": {
                "buckets": [
                    {"key": "INFO", "doc_count": 4917693},
                    {"key": "WARN", "doc_count": 391008},
                    {"key": "info", "doc_count": 3733},
                    {"key": "ERROR", "doc_count": 2999},
                    {"key": "DEBUG", "doc_count": 2824},
                ]
            }
        }
    }
    dist = parse_log_distribution(payload)
    assert dist.count("INFO") == 4917693 + 3733
    assert round(dist.pct("INFO"), 2) == 92.54


def test_extract_services_map() -> None:
    frames: list[dict[str, Any]] = [
        {
            "schema": {"fields": [{"name": "T"}, {"name": "V", "labels": {"service": "spi-main"}}]},
            "data": {"values": [[1], [19.32]]},
        },
        {
            "schema": {"fields": [{"name": "T"}, {"name": "V", "labels": {}}]},
            "data": {"values": [[1], [5.0]]},
        },
        {
            "schema": {"fields": [{"name": "T"}, {"name": "V", "labels": {"service": "spi-x"}}]},
            "data": {"values": [[1], [None]]},
        },
        {"schema": {"fields": [{"name": "T"}]}, "data": {"values": [[1]]}},
    ]
    assert extract_services_map(frames) == {"spi-main": 19.32}
