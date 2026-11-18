from __future__ import annotations

from datetime import date

from app.application.use_cases import (
    GenerateFlagshipReportCommand,
    GenerateFlagshipReportUseCase,
    GenerateRevolutReportCommand,
    GenerateRevolutReportUseCase,
)
from app.domain.flagship.models import HmlMetrics, PrdMetrics, RdsMetrics
from app.domain.revolut.models import RevolutReportData
from app.domain.time_window import TimeWindow, build_time_window, windows_up_to


class FakeOutput:
    def __init__(self) -> None:
        self.content = ""

    def write(self, content: str) -> None:
        self.content = content


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


def test_use_cases() -> None:
    w = build_time_window(date(2026, 11, 12), "08:30-10:30")
    ws = windows_up_to(date(2026, 11, 12), "08:30-10:30")

    out1 = FakeOutput()
    uc1 = GenerateFlagshipReportUseCase(FakeFlagshipReader(), FakeRdsReader(), out1)
    res1 = uc1.execute(GenerateFlagshipReportCommand(w, ws, skip_rds=True))
    assert "Coleta ignorada" in res1
    res1b = uc1.execute(GenerateFlagshipReportCommand(w, ws, skip_rds=False))
    assert "Sem dados disponíveis" in res1b

    out2 = FakeOutput()
    uc2 = GenerateRevolutReportUseCase(FakeRevolutReader(), out2)
    res2 = uc2.execute(GenerateRevolutReportCommand(w, ws))
    assert "Revolut" in res2
