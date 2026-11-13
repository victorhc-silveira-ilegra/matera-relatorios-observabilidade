from __future__ import annotations

from datetime import date
from typing import Any

import httpx
import pytest
from app.domain.flagship.models import LogDistribution
from app.domain.time_window import TimeWindow, build_time_window
from app.infrastructure.adapters import cloudwatch as cw_mod
from app.infrastructure.adapters import flagship_reader as fl_mod
from app.infrastructure.adapters import grafana as gf_mod
from app.infrastructure.adapters import opensearch as os_mod
from app.infrastructure.adapters import revolut_reader as rv_mod
from app.infrastructure.settings import Settings


def _dummy_settings() -> Settings:
    return Settings(
        kibana_hml_user="u",
        kibana_hml_pass="p",
        kibana_prd_user="u",
        kibana_prd_pass="p",
        grafana_user="u",
        grafana_pass="p",
        opensearch_hml_base="https://hml.example.com",
        opensearch_prd_base="https://prd.example.com",
        grafana_hml_base="https://gf-hml.example.com",
        grafana_prd_base="https://gf-prd.example.com",
        cloudwatch_rds_url="https://cloudwatch.amazonaws.com/dashboard.html?start=PT3H&end=null",
        grafana_revolut_user="u",
        grafana_revolut_pass="p",
        grafana_revolut_base="https://gf-rev.example.com",
        revolut_http_proxy="http://10.150.8.18:3128",
    )


def test_http_clients_with_mocks(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeResp:
        def __init__(self, data: dict[str, Any]) -> None:
            self._data = data

        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, Any]:
            return self._data

    class FakeHttpClient:
        def __init__(self, **kwargs: Any) -> None:
            pass

        def __enter__(self) -> FakeHttpClient:
            return self

        def __exit__(self, *args: Any) -> None:
            return None

        def post(self, url: str, **kwargs: Any) -> FakeResp:
            if "auth/login" in url:
                return FakeResp({})
            if "console/proxy" in url:
                return FakeResp(
                    {
                        "hits": {"total": {"value": 3}},
                        "aggregations": {"levels": {"buckets": [{"key": "INFO", "doc_count": 3}]}},
                    }
                )
            if "rawSql" in str(kwargs.get("json")):
                if "EMPTY_VALUES" in str(kwargs.get("json")):
                    return FakeResp(
                        {
                            "results": {
                                "A": {
                                    "frames": [
                                        {"data": {"values": []}},
                                        {"data": {"values": [[]]}},
                                    ]
                                }
                            }
                        }
                    )
                if "EMPTY" in str(kwargs.get("json")):
                    return FakeResp({"results": {"A": {"frames": [{"data": {"values": [[None]]}}]}}})
                if "NO_FRAMES" in str(kwargs.get("json")):
                    return FakeResp({"results": {"A": {"frames": []}}})
                return FakeResp({"results": {"A": {"frames": [{"data": {"values": [[7]]}}]}}})
            return FakeResp({"results": {"A": {"frames": [{"data": {"values": [[1], [5.0]]}}]}}})

    monkeypatch.setattr(httpx, "Client", FakeHttpClient)

    w = build_time_window(date(2026, 11, 12), "08:30-10:30")
    os_client = os_mod.OpenSearchClient("https://os.local", "u", "p")
    dist = os_client.fetch_log_distribution(w)
    assert dist.total == 3
    assert os_client.fetch_log_distribution(w, [{"term": {"a": "b"}}]).total == 3
    assert os_client.fetch_count(w, []) == 3

    gf_client = gf_mod.GrafanaClient("https://gf.local", "u", "p")
    assert len(gf_client.query_prometheus("up", w)) == 1
    assert gf_client.query_mysql_scalar("SELECT 1", "ds", w) == 7
    assert gf_client.query_mysql_scalar("SELECT EMPTY", "ds", w) is None
    assert gf_client.query_mysql_scalar("SELECT NO_FRAMES", "ds", w) is None
    assert gf_client.query_mysql_scalar("SELECT EMPTY_VALUES", "ds", w) is None


def test_flagship_and_revolut_adapters(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeOS:
        def __init__(self, **kwargs: Any) -> None:
            pass

        def fetch_log_distribution(
            self, window: TimeWindow, extra_filters: list[dict[str, Any]] | None = None
        ) -> LogDistribution:
            return LogDistribution(total=10, counts={"INFO": 10})

        def fetch_count(self, window: TimeWindow, filters: list[dict[str, Any]]) -> int:
            return 0

    class FakeGF:
        def __init__(self, **kwargs: Any) -> None:
            pass

        def query_prometheus(
            self, expr: str, window: TimeWindow, instant: bool = True, datasource_uid: str = "prometheus"
        ) -> list[dict[str, Any]]:
            if "logback_events_total" in expr:
                val = 150.0 if "[15m]" in expr else (100.0 if "NOT_NORMALIZED" in expr else 1.0)
                return [
                    {
                        "schema": {"fields": [{"name": "T"}, {"name": "V", "labels": {"service": "spi-main"}}]},
                        "data": {"values": [[1], [val]]},
                    }
                ]
            return [{"schema": {"fields": [{"name": "T"}, {"name": "V"}]}, "data": {"values": [[1], [1.0]]}}]

        def query_mysql_scalar(self, raw_sql: str, datasource_uid: str, window: TimeWindow) -> int:
            return 0

    monkeypatch.setattr(fl_mod, "OpenSearchClient", FakeOS)
    monkeypatch.setattr(fl_mod, "GrafanaClient", FakeGF)
    monkeypatch.setattr(rv_mod, "GrafanaClient", FakeGF)

    settings = _dummy_settings()
    w1 = build_time_window(date(2026, 11, 12), "08:30-10:30")
    w2 = build_time_window(date(2026, 11, 12), "10:30-13:30")
    w3 = build_time_window(date(2026, 11, 12), "13:30-16:30")

    fl = fl_mod.FlagshipMetricsAdapter(settings)
    assert fl.read_hml(w1).logs.total == 10
    assert fl.read_prd(w1, [w1]).saga_total == 0
    w_future = build_time_window(date(2099, 1, 1), "13:30-16:30")
    assert fl.read_hml(w_future).logs.total == 10
    assert fl.read_prd(w_future, [w_future]).saga_total == 0

    rv = rv_mod.RevolutMetricsAdapter(settings)
    rep1 = rv.read_revolut(w1, [w1], "V", "Sem ocorrências.")
    assert len(rep1.services_without_errors) == 12
    assert rep1.services_without_errors[5].value == 1.0

    class FakeGFUnnormalized(FakeGF):
        def query_prometheus(
            self, expr: str, window: TimeWindow, instant: bool = True, datasource_uid: str = "prometheus"
        ) -> list[dict[str, Any]]:
            if "logback_events_total" in expr:
                return [
                    {
                        "schema": {"fields": [{"name": "T"}, {"name": "V", "labels": {"service": "spi-main"}}]},
                        "data": {"values": [[1], [150.0]]},
                    }
                ]
            return [{"schema": {"fields": [{"name": "T"}, {"name": "V"}]}, "data": {"values": [[1], [1.0]]}}]

    monkeypatch.setattr(rv_mod, "GrafanaClient", FakeGFUnnormalized)
    rv_unnorm = rv_mod.RevolutMetricsAdapter(settings)
    assert len(rv_unnorm.read_revolut(w1, [w1], "V", "Sem ocorrências.").services_with_errors) == 1

    class FakeGFClean(FakeGF):
        def query_prometheus(
            self, expr: str, window: TimeWindow, instant: bool = True, datasource_uid: str = "prometheus"
        ) -> list[dict[str, Any]]:
            if "logback_events_total" in expr:
                return [
                    {
                        "schema": {"fields": [{"name": "T"}, {"name": "V", "labels": {"service": "spi-main"}}]},
                        "data": {"values": [[1], [0.0]]},
                    }
                ]
            return super().query_prometheus(expr, window, instant, datasource_uid)

    monkeypatch.setattr(rv_mod, "GrafanaClient", FakeGFClean)
    rv_clean = rv_mod.RevolutMetricsAdapter(settings)
    assert len(rv_clean.read_revolut(w1, [w1], "V", "Sem ocorrências.").services_with_errors) == 0

    monkeypatch.setattr(rv_mod, "GrafanaClient", FakeGF)
    w_future = build_time_window(date(2099, 1, 1), "13:30-16:30")
    assert len(rv.read_revolut(w_future, [w_future], "V", "Sem ocorrências.").services_without_errors) == 12
    assert "16:30h" in rv.read_revolut(w2, [w1, w2], "V", "Sem ocorrências.").next_analysis_label
    assert "proximo" in rv.read_revolut(w3, [w1, w2, w3], "V", "Sem ocorrências.").next_analysis_label.replace("ó", "o")

    bad_settings = Settings(**{**settings.__dict__, "grafana_revolut_user": ""})
    with pytest.raises(ValueError):
        rv_mod.RevolutMetricsAdapter(bad_settings)


def test_cloudwatch_adapter_with_mock_playwright(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeResp:
        def __init__(self, url: str, method: str, status: int, body: str) -> None:
            self.url = url
            self.request = type("Req", (), {"method": method})()
            self.status = status
            self._body = body

        def text(self) -> str:
            if self._body == "RAISE":
                raise RuntimeError("boom")
            return self._body

    class FakePage:
        def __init__(self, responses: list[FakeResp]) -> None:
            self._cb: Any = None
            self._responses = responses

        def on(self, event: str, cb: Any) -> None:
            self._cb = cb

        def goto(self, url: str, **kwargs: Any) -> None:
            for r in self._responses:
                self._cb(r)

        def wait_for_timeout(self, ms: int) -> None:
            return None

    class FakeBrowser:
        def __init__(self, responses: list[FakeResp]) -> None:
            self._responses = responses

        def new_page(self) -> FakePage:
            return FakePage(self._responses)

        def close(self) -> None:
            return None

    def make_pw(responses: list[FakeResp]) -> Any:
        class FakePW:
            def __enter__(self) -> FakePW:
                self.chromium = type(
                    "Chr",
                    (),
                    {"launch": lambda self, headless=True: FakeBrowser(responses)},
                )()
                return self

            def __exit__(self, *args: Any) -> None:
                return None

        return FakePW

    w = build_time_window(date(2026, 11, 12), "08:30-10:30")
    ok_json = '{"MetricData":[{"Label":"dtw-prod-cluster-transaction-1","Timestamps":[1],"Values":[42.0]}]}'
    monkeypatch.setattr(
        cw_mod,
        "sync_playwright",
        make_pw(
            [
                FakeResp("https://other.com", "GET", 200, ""),
                FakeResp("https://monitoring.sa-east-1.amazonaws.com/", "POST", 403, ""),
                FakeResp("https://monitoring.sa-east-1.amazonaws.com/", "POST", 200, "other"),
                FakeResp("https://monitoring.sa-east-1.amazonaws.com/", "POST", 200, "RAISE"),
                FakeResp("https://monitoring.sa-east-1.amazonaws.com/", "POST", 200, ok_json),
                FakeResp("https://monitoring.sa-east-1.amazonaws.com/", "POST", 200, ok_json),
            ]
        ),
    )
    adapter = cw_mod.CloudWatchRdsAdapter("https://cloudwatch.amazonaws.com/dashboard.html")
    res_ok = adapter.read_rds_cpu(w)
    assert res_ok.instances[0].current_pct == 42.0

    monkeypatch.setattr(cw_mod, "sync_playwright", make_pw([]))
    res_fail = adapter.read_rds_cpu(w)
    assert res_fail.error is not None
