from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.time_window import WindowCount


@dataclass
class LogDistribution:
    total: int = 0
    counts: dict[str, int] = field(default_factory=dict)

    def pct(self, level: str) -> float:
        if self.total <= 0:
            return 0.0
        return (self.counts.get(level, 0) / self.total) * 100.0

    def count(self, level: str) -> int:
        return self.counts.get(level, 0)


@dataclass(frozen=True)
class PodRestart:
    pod: str
    restarts: float


@dataclass
class HmlMetrics:
    logs: LogDistribution = field(default_factory=LogDistribution)
    incidents: float | None = None
    lag: float | None = None
    restarts: list[PodRestart] = field(default_factory=list)


@dataclass
class PrdMetrics:
    logs: LogDistribution = field(default_factory=LogDistribution)
    routing_errors_by_window: list[WindowCount] = field(default_factory=list)
    incidents: float | None = None
    lag: float | None = None
    restarts: list[PodRestart] = field(default_factory=list)
    saga_total: int | None = None
    saga_above_5m: int | None = None
    polling_processed: int | None = None
    polling_total: int | None = None
    api_hits_by_window: list[WindowCount] = field(default_factory=list)


@dataclass(frozen=True)
class RdsInstanceCpu:
    name: str
    current_pct: float | None
    peak_pct: float | None = None
    points_above_90: int = 0


@dataclass
class RdsMetrics:
    peaks_above_90: list[RdsInstanceCpu] = field(default_factory=list)
    instances: list[RdsInstanceCpu] = field(default_factory=list)
    error: str | None = None


@dataclass
class FlagshipReportData:
    date_label: str
    hour_label: str
    window_label: str
    hml: HmlMetrics = field(default_factory=HmlMetrics)
    prd: PrdMetrics = field(default_factory=PrdMetrics)
    rds: RdsMetrics = field(default_factory=RdsMetrics)
    chamados_hml: str = "Sem ocorrências."
    chamados_prd: str = "Sem ocorrências."
