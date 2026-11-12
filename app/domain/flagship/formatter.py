from __future__ import annotations

from app.domain.flagship.models import FlagshipReportData, PodRestart
from app.domain.flagship.status import (
    LAG_CRITICAL_THRESHOLD,
    LAG_IGNORE_THRESHOLD,
    POLLING_CRITICAL_THRESHOLD,
    POLLING_WARNING_THRESHOLD,
    RDS_SUSTAINED_POINTS,
    SAGA_WARNING_THRESHOLD,
    evaluate_hml_status,
    evaluate_prd_status,
)


def fmt_int(value: int | None) -> str:
    if value is None:
        return "No Data"
    return f"{value:,}".replace(",", ".")


def fmt_num(value: float | None) -> str:
    if value is None:
        return "No Data"
    if abs(value - round(value)) < 0.05:
        return fmt_int(int(round(value)))
    return f"{value:.1f}"


def fmt_restarts_block(title: str, restarts: list[PodRestart]) -> list[str]:
    if not restarts:
        return [f"{title}: Sem ocorrências"]
    lines = [f"{title}:  "]
    for r in restarts:
        lines.append(f"{r.pod} (Restarts = {r.restarts:.2f})  ")
    return lines


def format_flagship_report(data: FlagshipReportData) -> str:
    sep = "\n\n━━━━━━━━━━━━━━━━━━\n\n"
    sections: list[str] = []

    sections.append(f"📊 RELATÓRIO DTW — {data.date_label} às {data.hour_label}")
    sections.append("🏥 SAÚDE DO DTW")

    hml_logs = data.hml.logs
    hml_has_lag = data.hml.lag is not None and data.hml.lag > LAG_IGNORE_THRESHOLD
    hml_lag_txt = fmt_num(data.hml.lag) if hml_has_lag else "Sem ocorrências"
    hml_inc_txt = fmt_num(data.hml.incidents)
    hml_lines = [
        "🔧 AMBIENTE DE HOMOLOGAÇÃO (HML)",
        "",
        "📄 Logs  ",
        f"🟢 INFO: {hml_logs.pct('INFO'):.2f}%  ",
        f"🟡 WARN: {hml_logs.pct('WARN'):.2f}%  ",
        f"🔴 ERROR: {hml_logs.pct('ERROR'):.2f}%  ",
        f"🔵 DEBUG: {hml_logs.pct('DEBUG'):.2f}%",
        "",
        "📊 Outras Métricas  ",
        f"Incidentes (últimas 5h): {hml_inc_txt}  ",
        f"Lag: {hml_lag_txt}  ",
        *fmt_restarts_block("Restarts de pods (últimas 6h)", data.hml.restarts),
    ]
    sections.append("\n".join(hml_lines))

    prd_logs = data.prd.logs
    prd_err_count = fmt_int(prd_logs.count("ERROR"))
    prd_inc_txt = fmt_num(data.prd.incidents)
    prd_inc_emoji = " 🟢" if data.prd.incidents is not None else ""
    prd_has_lag = data.prd.lag is not None and data.prd.lag > LAG_IGNORE_THRESHOLD
    prd_lag_emoji = "🔴" if (data.prd.lag or 0) >= LAG_CRITICAL_THRESHOLD else "🟡"
    prd_lag_txt = f"{fmt_num(data.prd.lag)} {prd_lag_emoji}" if prd_has_lag else "Sem ocorrências"

    routing_lines = [f"{wc.window_label} → {fmt_int(wc.count)}  " for wc in data.prd.routing_errors_by_window]
    if routing_lines:
        routing_lines[-1] = routing_lines[-1].rstrip()

    prd_lines = [
        "🚀 AMBIENTE DE PRODUÇÃO (PRD)",
        "",
        "📄 Logs  ",
        f"🟢 INFO: {prd_logs.pct('INFO'):.2f}%  ",
        f"🟡 WARN: {prd_logs.pct('WARN'):.2f}%  ",
        f"🔴 ERROR: {prd_logs.pct('ERROR'):.2f}% ({prd_err_count})",
        "",
        "🛑 LOGS DE ERRO  ",
        "Serviço: cc-integration-event-routing-entry-producer  ",
        *routing_lines,
        "",
        "📊 Outras Métricas  ",
        f"Incidentes (últimos 30 min): {prd_inc_txt}{prd_inc_emoji}",
        "",
        f"Lag: {prd_lag_txt}",
        "",
        *fmt_restarts_block("Restarts", data.prd.restarts),
    ]
    sections.append("\n".join(prd_lines))

    saga_total = data.prd.saga_total
    saga_5m = data.prd.saga_above_5m
    saga_total_emoji = "🟢" if (saga_total or 0) < SAGA_WARNING_THRESHOLD else "🟡"
    saga_5m_emoji = "🟢" if (saga_5m or 0) == 0 else "🔴"
    saga_lines = [
        "🔄 INTEGRAÇÃO SAGA  ",
        f"Total de integrações: {fmt_int(saga_total)} {saga_total_emoji}  ",
        f"Integrações acima de 5 min: {fmt_int(saga_5m)} {saga_5m_emoji}",
    ]
    sections.append("\n".join(saga_lines))

    api_lines = [f"{wc.window_label} → {fmt_int(wc.count)} hits  " for wc in data.prd.api_hits_by_window]
    if api_lines:
        api_lines[-1] = api_lines[-1].rstrip()

    polling_total = data.prd.polling_total or 0
    if polling_total >= POLLING_CRITICAL_THRESHOLD:
        polling_emoji = "🔴"
    elif polling_total >= POLLING_WARNING_THRESHOLD:
        polling_emoji = "🟡"
    else:
        polling_emoji = "🟢"

    dados_lines = [
        "🗃️ MONITORAMENTO DE DADOS",
        "",
        "📥 Tabela DTWTRPOLLINGENTRY  ",
        f"Registros PROCESSED: {fmt_int(data.prd.polling_processed)} 🟢  ",
        f"Total de registros: {fmt_int(data.prd.polling_total)} {polling_emoji}",
        "",
        "📈 API Hits — dtw-transaction-api  ",
        *api_lines,
    ]
    sections.append("\n".join(dados_lines))

    rds_lines = [
        "🧠 RDS — CPU UTILIZATION",
        "",
        f"⏱ {data.window_label} (picos ≥ 90%)  ",
    ]
    if data.rds.error:
        rds_lines.append(f"Erro na coleta: {data.rds.error}")
    elif data.rds.peaks_above_90:
        for inst in data.rds.peaks_above_90:
            peak_emoji = (
                "🔴"
                if inst.points_above_90 >= RDS_SUSTAINED_POINTS
                or (inst.current_pct is not None and inst.current_pct >= 90.0)
                else "🟡"
            )
            rds_lines.append(f"{inst.name}: {inst.peak_pct:.3f}% {peak_emoji}  ")
        rds_lines[-1] = rds_lines[-1].rstrip()
    else:
        rds_lines.append("Sem ocorrências")

    rds_lines.extend(["", "📉 CONSUMO ATUAL  "])
    if data.rds.instances:
        for inst in data.rds.instances:
            val_txt = f"{inst.current_pct:.3f}%" if inst.current_pct is not None else "No Data"
            rds_lines.append(f"{inst.name}: {val_txt}  ")
        rds_lines[-1] = rds_lines[-1].rstrip()
    else:
        rds_lines.append("Sem dados disponíveis")
    sections.append("\n".join(rds_lines))

    chamados_lines = [
        "🧾 CHAMADOS EM ANDAMENTO  ",
        f"🔹 HML: {data.chamados_hml}  ",
        f"🔹 PRD: {data.chamados_prd}",
    ]
    sections.append("\n".join(chamados_lines))

    prd_status = evaluate_prd_status(data)
    hml_status = evaluate_hml_status(data)

    status_lines = [
        "📌 STATUS DOS AMBIENTES  ",
        f"Produção (PRD): {prd_status.label}  ",
        f"Homologação (HML): {hml_status.label}",
    ]
    sections.append("\n".join(status_lines))

    return sep.join(sections)
