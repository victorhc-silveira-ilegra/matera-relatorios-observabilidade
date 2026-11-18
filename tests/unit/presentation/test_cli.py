from __future__ import annotations

import runpy
import sys

import pytest
from app.domain.flagship.models import HmlMetrics, PrdMetrics, RdsMetrics
from app.domain.revolut.models import RevolutReportData
from app.domain.time_window import TimeWindow
from app.infrastructure.settings import Settings
from app.presentation import cli as cli_mod


class FakeFlagshipReader:
    def read_hml(self, window: TimeWindow) -> HmlMetrics:
        return HmlMetrics()

    def read_prd(self, current_window: TimeWindow, day_windows: list[TimeWindow]) -> PrdMetrics:
        return PrdMetrics()


class FakeRdsReader:
    def read_rds_cpu(self, window: TimeWindow) -> RdsMetrics:
        return RdsMetrics()


class FakeRevolutReader:
    def read_revolut(
        self,
        current_window: TimeWindow,
        day_windows: list[TimeWindow],
        responsavel: str,
        chamados: str,
    ) -> RevolutReportData:
        return RevolutReportData(
            date_full="12/11/2026",
            period_label="08:30h - 10:30h",
            current_window_label=current_window.label,
            responsavel=responsavel,
            chamados=chamados,
            next_analysis_label="12/11/2026 às 13:30h",
        )


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


def test_cli_entrypoint(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.infrastructure.settings.load_settings", _dummy_settings)
    monkeypatch.setattr(
        "app.infrastructure.adapters.flagship_reader.FlagshipMetricsAdapter",
        lambda s: FakeFlagshipReader(),
    )
    monkeypatch.setattr(
        "app.infrastructure.adapters.cloudwatch.CloudWatchRdsAdapter",
        lambda u: FakeRdsReader(),
    )
    monkeypatch.setattr(
        "app.infrastructure.adapters.revolut_reader.RevolutMetricsAdapter",
        lambda s: FakeRevolutReader(),
    )

    monkeypatch.setattr(cli_mod, "load_settings", _dummy_settings)
    monkeypatch.setattr(cli_mod, "FlagshipMetricsAdapter", lambda s: FakeFlagshipReader())
    monkeypatch.setattr(cli_mod, "CloudWatchRdsAdapter", lambda u: FakeRdsReader())
    monkeypatch.setattr(cli_mod, "RevolutMetricsAdapter", lambda s: FakeRevolutReader())

    assert cli_mod.main(["--client", "flagship", "--date", "2026-11-12", "--window", "08:30-10:30"]) == 0
    assert cli_mod.main(["--client", "revolut", "--window", "08:30-10:30"]) == 0

    monkeypatch.setattr(sys, "argv", ["cli", "--client", "revolut", "--window", "08:30-10:30"])
    with pytest.raises(SystemExit) as exc_info:
        runpy.run_module("app.presentation.cli", run_name="__main__")
    assert exc_info.value.code == 0
