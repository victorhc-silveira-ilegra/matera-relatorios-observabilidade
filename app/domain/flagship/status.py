from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from app.domain.flagship.models import FlagshipReportData

LAG_IGNORE_THRESHOLD = 10.0
LAG_CRITICAL_THRESHOLD = 1000.0
RESTART_CRITICAL_THRESHOLD = 3.0
POLLING_WARNING_THRESHOLD = 100
POLLING_CRITICAL_THRESHOLD = 10000
RDS_SUSTAINED_POINTS = 3
PRD_ERROR_WARNING_PCT = 5.0
PRD_ERROR_CRITICAL_PCT = 50.0
PRD_WARN_WARNING_PCT = 20.0
ROUTING_ERROR_WARNING_THRESHOLD = 10
API_HITS_WARNING_THRESHOLD = 10
SAGA_WARNING_THRESHOLD = 10


class HealthLevel(StrEnum):
    STABLE = "STABLE"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

    @property
    def label(self) -> str:
        if self is HealthLevel.CRITICAL:
            return "🔴 Instável"
        if self is HealthLevel.WARNING:
            return "🟡 Atenção"
        return "🟢 Estável"


@dataclass(frozen=True)
class EnvironmentStatus:
    level: HealthLevel
    reasons: list[str]

    @property
    def label(self) -> str:
        return self.level.label


def has_active_ticket(chamados_text: str) -> bool:
    normalized = chamados_text.strip().lower().rstrip(".")
    return bool(normalized) and normalized not in {"sem ocorrências", "sem ocorrencias", "nenhum"}


def evaluate_prd_status(data: FlagshipReportData) -> EnvironmentStatus:
    critical_reasons: list[str] = []
    warning_reasons: list[str] = []

    prd = data.prd
    err_pct = prd.logs.pct("ERROR")
    warn_pct = prd.logs.pct("WARN")

    if err_pct >= PRD_ERROR_CRITICAL_PCT:
        critical_reasons.append(f"ERROR predominante ({err_pct:.2f}%)")
    elif err_pct >= PRD_ERROR_WARNING_PCT:
        warning_reasons.append(f"ERROR elevado ({err_pct:.2f}%)")

    if warn_pct >= PRD_WARN_WARNING_PCT:
        warning_reasons.append(f"WARN elevado ({warn_pct:.2f}%)")

    if prd.routing_errors_by_window and prd.routing_errors_by_window[-1].count >= ROUTING_ERROR_WARNING_THRESHOLD:
        warning_reasons.append("Erros recorrentes em cc-integration-event-routing-entry-producer")

    if prd.api_hits_by_window and prd.api_hits_by_window[-1].count >= API_HITS_WARNING_THRESHOLD:
        warning_reasons.append("API Hits recorrentes de erro em dtw-transaction-api")

    if prd.lag is not None:
        if prd.lag >= LAG_CRITICAL_THRESHOLD:
            critical_reasons.append(f"Lag massivo ({prd.lag:.0f})")
        elif prd.lag > LAG_IGNORE_THRESHOLD:
            warning_reasons.append(f"Lag moderado ({prd.lag:.0f})")

    max_restarts = max((r.restarts for r in prd.restarts), default=0.0)
    if max_restarts >= RESTART_CRITICAL_THRESHOLD:
        critical_reasons.append(f"Crash loop em pod (restarts={max_restarts:.2f})")
    elif max_restarts > 0:
        warning_reasons.append(f"Restarts pontuais de pods ({max_restarts:.2f})")

    if prd.saga_above_5m and prd.saga_above_5m > 0:
        critical_reasons.append(f"SAGA > 5 min ({prd.saga_above_5m})")
    elif prd.saga_total and prd.saga_total >= SAGA_WARNING_THRESHOLD:
        warning_reasons.append(f"Integrações SAGA pendentes ({prd.saga_total})")

    if prd.polling_total is not None:
        if prd.polling_total >= POLLING_CRITICAL_THRESHOLD:
            critical_reasons.append(f"Polling acumulado crítico ({prd.polling_total})")
        elif prd.polling_total >= POLLING_WARNING_THRESHOLD:
            warning_reasons.append(f"Polling acumulado moderado ({prd.polling_total})")

    for inst in data.rds.peaks_above_90:
        if inst.points_above_90 >= RDS_SUSTAINED_POINTS or (inst.current_pct is not None and inst.current_pct >= 90.0):
            critical_reasons.append(f"RDS CPU sustentado >= 90% ({inst.name})")
        else:
            warning_reasons.append(f"RDS CPU pico pontual >= 90% ({inst.name})")

    if has_active_ticket(data.chamados_prd):
        warning_reasons.append("Chamado ativo em PRD")

    if critical_reasons:
        return EnvironmentStatus(HealthLevel.CRITICAL, critical_reasons)
    if warning_reasons:
        return EnvironmentStatus(HealthLevel.WARNING, warning_reasons)
    return EnvironmentStatus(HealthLevel.STABLE, [])


def evaluate_hml_status(data: FlagshipReportData) -> EnvironmentStatus:
    critical_reasons: list[str] = []
    warning_reasons: list[str] = []

    hml = data.hml

    if hml.lag is not None:
        if hml.lag >= LAG_CRITICAL_THRESHOLD:
            critical_reasons.append(f"Lag massivo ({hml.lag:.0f})")
        elif hml.lag > LAG_IGNORE_THRESHOLD:
            warning_reasons.append(f"Lag moderado ({hml.lag:.0f})")

    max_restarts = max((r.restarts for r in hml.restarts), default=0.0)
    if max_restarts >= RESTART_CRITICAL_THRESHOLD:
        critical_reasons.append(f"Crash loop em pod (restarts={max_restarts:.2f})")
    elif max_restarts > 0:
        warning_reasons.append(f"Restarts pontuais de pods ({max_restarts:.2f})")

    if has_active_ticket(data.chamados_hml):
        warning_reasons.append("Chamado ativo em HML")

    if critical_reasons:
        return EnvironmentStatus(HealthLevel.CRITICAL, critical_reasons)
    if warning_reasons:
        return EnvironmentStatus(HealthLevel.WARNING, warning_reasons)
    return EnvironmentStatus(HealthLevel.STABLE, [])
