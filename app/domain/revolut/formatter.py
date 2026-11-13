from __future__ import annotations

from app.domain.revolut.models import RevolutReportData

PAGADOR_P50_LIMIT_S = 0.9
PAGADOR_P95_LIMIT_S = 1.5
RECEBEDOR_P50_LIMIT_S = 1.4
RECEBEDOR_P95_LIMIT_S = 2.3


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


def latency_badge(seconds: float | None, limit_s: float) -> str:
    if seconds is None:
        return "⚠️"
    if seconds <= limit_s:
        return "✅"
    if seconds <= limit_s * 1.25:
        return "🟡"
    return "🔴"


def format_revolut_report(data: RevolutReportData) -> str:
    pag_p50 = data.pagador_latency.p50_seconds
    pag_p95 = data.pagador_latency.p95_seconds
    rec_p50 = data.recebedor_latency.p50_seconds
    rec_p95 = data.recebedor_latency.p95_seconds

    pag_p50_badge = latency_badge(pag_p50, PAGADOR_P50_LIMIT_S)
    pag_p95_badge = latency_badge(pag_p95, PAGADOR_P95_LIMIT_S)
    rec_p50_badge = latency_badge(rec_p50, RECEBEDOR_P50_LIMIT_S)
    rec_p95_badge = latency_badge(rec_p95, RECEBEDOR_P95_LIMIT_S)

    total_services = len(data.services_with_errors) + len(data.services_without_errors)
    err_count = len(data.services_with_errors)
    ok_count = len(data.services_without_errors)

    all_latencies_ok = all(b == "✅" for b in (pag_p50_badge, pag_p95_badge, rec_p50_badge, rec_p95_badge))
    has_critical_latency = any(b == "🔴" for b in (pag_p50_badge, pag_p95_badge, rec_p50_badge, rec_p95_badge))
    has_ticket = data.chamados.strip().lower().rstrip(".") not in {
        "sem ocorrências",
        "sem ocorrencias",
        "",
    }

    if has_critical_latency:
        status_line = "Ambiente instável 🔴 (Ocorrências críticas identificadas no período)."
        eventos_line = f"Identificados {err_count} serviço(s) com erros nos logs ou latência fora do limite crítico."
        period_badge = "🔴"
    elif err_count > 0 or not all_latencies_ok or has_ticket:
        if err_count > 0:
            status_line = "Ambiente em atenção 🟡 (Ocorrências nos logs identificadas no período em acompanhamento)."
            eventos_line = f"Identificados {err_count} serviço(s) com erros nos logs em acompanhamento contínuo."
        else:
            status_line = "Ambiente em atenção 🟡 (Desvio pontual de latência ou chamado ativo em acompanhamento)."
            eventos_line = "Monitoramento ativo para desvios pontuais de latência ou chamados abertos."
        period_badge = "🟡"
    else:
        status_line = (
            "Ambiente estável ✅ (Sem ocorrências de erros registradas nos logs e métricas dentro da normalidade)."
        )
        eventos_line = (
            f"Nenhum evento crítico identificado no período. Todos os {total_services} serviços operaram "
            "sem registro de falhas nos logs e com as latências mantidas dentro dos patamares ideais."
        )
        period_badge = "✅"

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

    all_slots = ["08:30h - 10:30h", "10:30h - 13:30h", "13:30h - 16:30h"]
    slot_rows: list[str] = []
    passed_current = False
    for slot in all_slots:
        if not passed_current:
            badge = period_badge if slot == data.period_label else "✅"
            slot_rows.append(f"{slot}  {badge}         0                   Não")
            if slot == data.period_label:
                passed_current = True
        else:
            slot_rows.append(slot)

    lines = [
        "📊 Relatório - Observabilidade | Revolut",
        f"📅 Data: {data.date_full}",
        f"👤 Responsável: {data.responsavel}",
        "🧩 Aplicação: MIP",
        "🌍 Ambiente: Produção",
        "☁️ Cloud Provider: AWS",
        f"⏰ Período: {data.period_label}",
        "",
        "Status Geral do Ambiente",
        status_line,
        "",
        "📌 Eventos Identificados",
        eventos_line,
        "",
        "⚡ Tempos de Processamento PIX",
        "Métrica     Pagador         Recebedor",
        f"P50         {fmt_duration(pag_p50)} {pag_p50_badge:<6}   {fmt_duration(rec_p50)} {rec_p50_badge}",
        f"P95         {fmt_duration(pag_p95)} {pag_p95_badge:<6}   {fmt_duration(rec_p95)} {rec_p95_badge}",
        "",
        f"(Observação: Latência do Pagador apresentou P50 em {fmt_duration(pag_p50)} e P95 em {fmt_duration(pag_p95)}. "
        f"No Recebedor, o P50 registrou {fmt_duration(rec_p50)} e o P95 manteve-se em {fmt_duration(rec_p95)}.)",
        "",
        "💰 PIXs recebidos Recebedor (aproximado)",
        *rec_lines,
        "",
        "💰 PIXs recebidos Pagador (aproximado)",
        *pag_lines,
        "",
        "Quantidade de Erros nos Logs (últimos 15m)",
        "🔴 Com Erros:",
        *with_err_lines,
        "",
        "✅ Sem Erros:",
        *without_err_lines,
        "",
        "📊 Resumo:",
        f"Total de serviços analisados: {total_services}",
        f"Serviços com erro: {err_count}",
        f"Serviços sem erro: {ok_count}",
        "",
        "🛠️ Comentários Técnicos",
        f"Acompanhamento contínuo. {'Normalização total nos logs' if err_count == 0 else 'Atenção aos logs de erro'}, "
        f"com os {total_services} serviços do SPI analisados. Registrado volume de {fmt_int_br(latest_rec)} transações "
        f"no Recebedor e {fmt_int_br(latest_pag)} no Pagador na janela {data.period_label}, mantendo o acompanhamento "
        "das latências (P50 e P95).",
        "",
        "📞 Chamados Acompanhados",
        data.chamados,
        "",
        "📊 Status por Horário",
        "Horário          Status    Eventos Críticos    Intervenção Manual",
        *slot_rows,
        "",
        "📌 Notas Finais",
        f"Nenhum incidente reportado por clientes. A próxima análise está prevista para {data.next_analysis_label}.",
    ]
    return "\n".join(lines)
