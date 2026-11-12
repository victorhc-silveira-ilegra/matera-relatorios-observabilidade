from __future__ import annotations

from dataclasses import dataclass

from app.application.ports import (
    FlagshipMetricsReader,
    RdsMetricsReader,
    ReportOutputPort,
    RevolutMetricsReader,
)
from app.domain.flagship.formatter import format_flagship_report
from app.domain.flagship.models import FlagshipReportData, RdsMetrics
from app.domain.revolut.formatter import format_revolut_report
from app.domain.time_window import TimeWindow


@dataclass(frozen=True)
class GenerateFlagshipReportCommand:
    current_window: TimeWindow
    day_windows: list[TimeWindow]
    chamados_hml: str = "Sem ocorrências."
    chamados_prd: str = "Sem ocorrências."
    skip_rds: bool = False


class GenerateFlagshipReportUseCase:
    def __init__(
        self,
        metrics_reader: FlagshipMetricsReader,
        rds_reader: RdsMetricsReader,
        output_port: ReportOutputPort,
    ) -> None:
        self._metrics_reader = metrics_reader
        self._rds_reader = rds_reader
        self._output_port = output_port

    def execute(self, command: GenerateFlagshipReportCommand) -> str:
        hml = self._metrics_reader.read_hml(command.current_window)
        prd = self._metrics_reader.read_prd(command.current_window, command.day_windows)
        if command.skip_rds:
            rds = RdsMetrics(error="Coleta ignorada (--skip-rds).")
        else:
            rds = self._rds_reader.read_rds_cpu(command.current_window)

        report_data = FlagshipReportData(
            date_label=command.current_window.date_label,
            hour_label=command.current_window.end_hour_label,
            window_label=command.current_window.label,
            hml=hml,
            prd=prd,
            rds=rds,
            chamados_hml=command.chamados_hml,
            chamados_prd=command.chamados_prd,
        )
        rendered = format_flagship_report(report_data)
        self._output_port.write(rendered)
        return rendered


@dataclass(frozen=True)
class GenerateRevolutReportCommand:
    current_window: TimeWindow
    day_windows: list[TimeWindow]
    responsavel: str = "Victor Silveira"
    chamados: str = "Sem ocorrências."


class GenerateRevolutReportUseCase:
    def __init__(
        self,
        metrics_reader: RevolutMetricsReader,
        output_port: ReportOutputPort,
    ) -> None:
        self._metrics_reader = metrics_reader
        self._output_port = output_port

    def execute(self, command: GenerateRevolutReportCommand) -> str:
        report_data = self._metrics_reader.read_revolut(
            current_window=command.current_window,
            day_windows=command.day_windows,
            responsavel=command.responsavel,
            chamados=command.chamados,
        )
        rendered = format_revolut_report(report_data)
        self._output_port.write(rendered)
        return rendered
