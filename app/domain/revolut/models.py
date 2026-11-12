from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.time_window import WindowCount


@dataclass(frozen=True)
class RevolutLatency:
    p50_seconds: float | None = None
    p95_seconds: float | None = None


@dataclass(frozen=True)
class RevolutServiceError:
    service: str
    value: float


@dataclass
class RevolutReportData:
    date_full: str
    period_label: str
    current_window_label: str
    responsavel: str = "Victor Silveira"
    pagador_latency: RevolutLatency = field(default_factory=RevolutLatency)
    recebedor_latency: RevolutLatency = field(default_factory=RevolutLatency)
    recebedor_pix_by_window: list[WindowCount] = field(default_factory=list)
    pagador_pix_by_window: list[WindowCount] = field(default_factory=list)
    services_with_errors: list[RevolutServiceError] = field(default_factory=list)
    services_without_errors: list[RevolutServiceError] = field(default_factory=list)
    chamados: str = "Sem ocorrências."
    next_analysis_label: str = ""
