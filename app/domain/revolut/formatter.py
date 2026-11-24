from __future__ import annotations

from dataclasses import dataclass

from app.domain.revolut.models import (
    RevolutHttpError,
    RevolutLatency,
    RevolutPodRestart,
    RevolutReportData,
    RevolutServiceError,
)
from app.domain.time_window import DAILY_WINDOWS, WINDOW_ORDER

HTTP_5XX_CRITICAL_THRESHOLD = 80
RESTART_CRITICAL_THRESHOLD = 3.0


@dataclass(frozen=True)
class LatencyThreshold:
    warning_s: float
    critical_s: float


PAGADOR_P50_THRESHOLD = LatencyThreshold(warning_s=0.6, critical_s=0.9)
PAGADOR_P95_THRESHOLD = LatencyThreshold(warning_s=1.2, critical_s=1.5)
RECEBEDOR_P50_THRESHOLD = LatencyThreshold(warning_s=1.0, critical_s=1.3)
RECEBEDOR_P95_THRESHOLD = LatencyThreshold(warning_s=2.0, critical_s=2.4)


def fmt_duration(seconds: float | None) -> str:
    if seconds is None:
        return "No Data"
    if seconds < 1.0:
        return f"{seconds * 1000:.2f}ms".replace(".00ms", "ms")
    return f"{seconds:.3f}s"


def fmt_int_br(value: int) -> str:
    return f"{value:,}".replace(",", ".")


def fmt_log_val(val: float) -> str:
    if abs(val) < 0.005:
        return "0"
    if val >= 100:
        return f"{val:.1f}"
    return f"{val:.2f}".rstrip("0").rstrip(".")


def latency_badge(seconds: float | None, threshold: LatencyThreshold) -> str:
    if seconds is None:
        return "⚠️"
    if seconds < threshold.warning_s:
        return "✅"
    if seconds < threshold.critical_s:
        return "🟡"
    return "🔴"


@dataclass(frozen=True)
class RevolutStatusEvaluation:
    status_line: str
    eventos_line: str
    badge: str
    critical_events: int
    critical_details: tuple[str, ...]


def evaluate_revolut_status(
    pagador_latency: RevolutLatency,
    recebedor_latency: RevolutLatency,
    err_count: int,
    total_services: int,
    has_ticket: bool,
    services_with_errors: tuple[RevolutServiceError, ...] = (),
    restarts: tuple[RevolutPodRestart, ...] = (),
    http_5xx_errors: tuple[RevolutHttpError, ...] = (),
) -> RevolutStatusEvaluation:
    pag_p50_badge = latency_badge(pagador_latency.p50_seconds, PAGADOR_P50_THRESHOLD)
    pag_p95_badge = latency_badge(pagador_latency.p95_seconds, PAGADOR_P95_THRESHOLD)
    rec_p50_badge = latency_badge(recebedor_latency.p50_seconds, RECEBEDOR_P50_THRESHOLD)
    rec_p95_badge = latency_badge(recebedor_latency.p95_seconds, RECEBEDOR_P95_THRESHOLD)

    named_metrics = (
        (pag_p50_badge, "Pagador P50", pagador_latency.p50_seconds),
        (pag_p95_badge, "Pagador P95", pagador_latency.p95_seconds),
        (rec_p50_badge, "Recebedor P50", recebedor_latency.p50_seconds),
        (rec_p95_badge, "Recebedor P95", recebedor_latency.p95_seconds),
    )
    all_latencies_ok = all(b == "✅" for b, _, _ in named_metrics)
    critical_latency_details = tuple(f"{name}: {fmt_duration(val)}" for b, name, val in named_metrics if b == "🔴")
    service_error_details = tuple(f"{s.service}: {fmt_log_val(s.value)}" for s in services_with_errors)
    critical_restart_details = tuple(
        f"{r.pod} restarts: {int(round(r.restarts))}" for r in restarts if r.restarts >= RESTART_CRITICAL_THRESHOLD
    )
    critical_5xx_details = tuple(
        f"{e.service} 5XX: {e.count}" for e in http_5xx_errors if e.count >= HTTP_5XX_CRITICAL_THRESHOLD
    )
    critical_details = (
        critical_latency_details + service_error_details + critical_restart_details + critical_5xx_details
    )
    critical_events = (
        err_count + len(critical_latency_details) + len(critical_restart_details) + len(critical_5xx_details)
    )

    if critical_latency_details or critical_restart_details or critical_5xx_details:
        status_line = "Ambiente em atenção 🟡 (Ocorrências críticas identificadas no período)."
        if err_count > 0:
            eventos_line = f"Identificados {err_count} serviço(s) com erros nos logs e latência fora do limite crítico."
        else:
            eventos_line = "Ocorrência crítica identificada no período (sem erros nos logs)."
        return RevolutStatusEvaluation(status_line, eventos_line, "🔴", critical_events, critical_details)

    if err_count > 0 or not all_latencies_ok or has_ticket or restarts or http_5xx_errors:
        if err_count > 0:
            status_line = "Ambiente em atenção 🟡 (Ocorrências nos logs identificadas no período em acompanhamento)."
            eventos_line = f"Identificados {err_count} serviço(s) com erros nos logs em acompanhamento contínuo."
        else:
            status_line = "Ambiente em atenção 🟡 (Desvio pontual identificado ou chamado ativo em acompanhamento)."
            eventos_line = "Monitoramento ativo para desvios pontuais de latência, restarts, 5XX ou chamados abertos."
        return RevolutStatusEvaluation(status_line, eventos_line, "🟡", critical_events, critical_details)

    status_line = (
        "Ambiente estável ✅ (Sem ocorrências de erros registradas nos logs e métricas dentro da normalidade)."
    )
    eventos_line = (
        f"Nenhum evento crítico identificado no período. Todos os {total_services} serviços operaram "
        "sem registro de falhas nos logs e com as latências mantidas dentro dos patamares ideais."
    )
    return RevolutStatusEvaluation(status_line, eventos_line, "✅", 0, ())


def format_revolut_report(data: RevolutReportData) -> str:
    pag_p50 = data.pagador_latency.p50_seconds
    pag_p95 = data.pagador_latency.p95_seconds
    rec_p50 = data.recebedor_latency.p50_seconds
    rec_p95 = data.recebedor_latency.p95_seconds

    pag_p50_badge = latency_badge(pag_p50, PAGADOR_P50_THRESHOLD)
    pag_p95_badge = latency_badge(pag_p95, PAGADOR_P95_THRESHOLD)
    rec_p50_badge = latency_badge(rec_p50, RECEBEDOR_P50_THRESHOLD)
    rec_p95_badge = latency_badge(rec_p95, RECEBEDOR_P95_THRESHOLD)

    total_services = len(data.services_with_errors) + len(data.services_without_errors)
    err_count = len(data.services_with_errors)
    ok_count = len(data.services_without_errors)

    has_ticket = data.chamados.strip().lower().rstrip(".") not in {
        "sem ocorrências",
        "sem ocorrencias",
        "",
    }
    evaluation = evaluate_revolut_status(
        pagador_latency=data.pagador_latency,
        recebedor_latency=data.recebedor_latency,
        err_count=err_count,
        total_services=total_services,
        has_ticket=has_ticket,
        services_with_errors=tuple(data.services_with_errors),
        restarts=tuple(data.restarts),
        http_5xx_errors=tuple(data.http_5xx_errors),
    )

    restart_lines: list[str] = (
        [
            f"• **{r.pod}:** {int(round(r.restarts))} restarts "
            f"{'🔴' if r.restarts >= RESTART_CRITICAL_THRESHOLD else '🟡'}"
            for r in data.restarts
        ]
        if data.restarts
        else ["Sem ocorrências ✅"]
    )
    http_5xx_lines: list[str] = (
        [
            f"• **{e.service}:** {fmt_int_br(e.count)} {'🔴' if e.count >= HTTP_5XX_CRITICAL_THRESHOLD else '🟡'}"
            for e in data.http_5xx_errors
        ]
        if data.http_5xx_errors
        else ["Sem ocorrências ✅"]
    )

    rec_lines = [f"{wc.window_label} - {wc.count}" for wc in data.recebedor_pix_by_window]
    pag_lines = [f"{wc.window_label} - {wc.count}" for wc in data.pagador_pix_by_window]

    with_err_lines: list[str] = (
        [f"{s.service} - {fmt_log_val(s.value)} 🔴" for s in data.services_with_errors]
        if data.services_with_errors
        else ["Sem erros"]
    )
    without_err_lines: list[str] = [
        f"{s.service:<35} {fmt_log_val(s.value):>6} ✅" for s in data.services_without_errors
    ]

    latest_rec = data.recebedor_pix_by_window[-1].count if data.recebedor_pix_by_window else 0
    latest_pag = data.pagador_pix_by_window[-1].count if data.pagador_pix_by_window else 0

    status_by_slot = {ws.period_label: ws for ws in data.window_statuses}
    all_slots = [f"{DAILY_WINDOWS[k][0]}h - {DAILY_WINDOWS[k][1]}h" for k in WINDOW_ORDER]
    slot_rows: list[str] = []
    detail_lines: list[str] = []
    passed_current = False
    for slot in all_slots:
        if not passed_current:
            if slot == data.period_label:
                badge, crit, details = evaluation.badge, evaluation.critical_events, evaluation.critical_details
                passed_current = True
            elif slot in status_by_slot:
                ws = status_by_slot[slot]
                badge, crit, details = ws.badge, ws.critical_events, ws.critical_event_details
            else:
                badge, crit, details = "✅", 0, ()
            slot_rows.append(f"{slot}  {badge}         {crit:<19} Não")
            if details:
                formatted_details = " | ".join(f"{item} 🔴" for item in details)
                detail_lines.append(f"• **{slot}:** {formatted_details}")
        else:
            slot_rows.append(slot)

    lines = [
        "📊 **Relatório - Observabilidade | Revolut**",
        f"📅 **Data:** {data.date_full}",
        f"👤 **Responsável:** {data.responsavel}",
        "🧩 **Aplicação:** MIP",
        "🌍 **Ambiente:** Produção",
        "☁️ **Cloud Provider:** AWS",
        f"⏰ **Período:** {data.period_label}",
        "",
        "**Status Geral do Ambiente**",
        evaluation.status_line,
        "",
        "📌 **Eventos Identificados**",
        evaluation.eventos_line,
        "",
        "⚡ **Tempos de Processamento PIX**",
        "Métrica     Pagador         Recebedor",
        f"P50         {fmt_duration(pag_p50)} {pag_p50_badge:<6}   {fmt_duration(rec_p50)} {rec_p50_badge}",
        f"P95         {fmt_duration(pag_p95)} {pag_p95_badge:<6}   {fmt_duration(rec_p95)} {rec_p95_badge}",
        "",
        f"(Observação: Latência do Pagador apresentou P50 em {fmt_duration(pag_p50)} e P95 em {fmt_duration(pag_p95)}. "
        f"No Recebedor, o P50 registrou {fmt_duration(rec_p50)} e o P95 manteve-se em {fmt_duration(rec_p95)}.)",
        "",
        "💰 **PIXs recebidos Recebedor (aproximado)**",
        *rec_lines,
        "",
        "💰 **PIXs recebidos Pagador (aproximado)**",
        *pag_lines,
        "",
        "**Quantidade de Erros nos Logs (últimos 15m)**",
        "🔴 **Com Erros:**",
        *with_err_lines,
        "",
        "✅ **Sem Erros:**",
        *without_err_lines,
        "",
        "🔄 **Restarts de Pods**",
        *restart_lines,
        "",
        "🌐 **Erros HTTP 5XX**",
        *http_5xx_lines,
        "",
        "📊 **Resumo:**",
        f"**Total de serviços analisados:** {total_services}",
        f"**Serviços com erro:** {err_count}",
        f"**Serviços sem erro:** {ok_count}",
        "",
        "🛠️ **Comentários Técnicos**",
        f"Acompanhamento contínuo. {'Normalização total nos logs' if err_count == 0 else 'Atenção aos logs de erro'}, "
        f"com os {total_services} serviços do SPI analisados. Registrado volume de {fmt_int_br(latest_rec)} transações "
        f"no Recebedor e {fmt_int_br(latest_pag)} no Pagador na janela {data.period_label}, mantendo o acompanhamento "
        "das latências (P50 e P95).",
        "",
        "📞 **Chamados Acompanhados**",
        data.chamados,
        "",
        "📊 **Status por Horário**",
        "Horário          Status    Eventos Críticos    Intervenção Manual",
        *slot_rows,
        *(["", "🔎 **Detalhes dos Eventos Críticos**", *detail_lines] if detail_lines else []),
        "",
        "📌 **Notas Finais**",
        f"Nenhum incidente reportado por clientes. A próxima análise está prevista para {data.next_analysis_label}.",
    ]
    return "\n".join(lines)
