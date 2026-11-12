from __future__ import annotations

from typing import Protocol

from app.domain.flagship.models import HmlMetrics, PrdMetrics, RdsMetrics
from app.domain.revolut.models import RevolutReportData
from app.domain.time_window import TimeWindow


class FlagshipMetricsReader(Protocol):
    def read_hml(self, window: TimeWindow) -> HmlMetrics: ...

    def read_prd(self, current_window: TimeWindow, day_windows: list[TimeWindow]) -> PrdMetrics: ...


class RdsMetricsReader(Protocol):
    def read_rds_cpu(self, window: TimeWindow) -> RdsMetrics: ...


class RevolutMetricsReader(Protocol):
    def read_revolut(
        self,
        current_window: TimeWindow,
        day_windows: list[TimeWindow],
        responsavel: str,
        chamados: str,
    ) -> RevolutReportData: ...


class ReportOutputPort(Protocol):
    def write(self, content: str) -> None: ...
