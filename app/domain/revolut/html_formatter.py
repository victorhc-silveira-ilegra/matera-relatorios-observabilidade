from __future__ import annotations

from app.domain.revolut.formatter import (
    PAGADOR_P50_LIMIT_S,
    PAGADOR_P95_LIMIT_S,
    RECEBEDOR_P50_LIMIT_S,
    RECEBEDOR_P95_LIMIT_S,
    fmt_duration,
    fmt_int_br,
    fmt_log_val,
    latency_badge,
)
from app.domain.revolut.models import RevolutReportData


def format_revolut_html(data: RevolutReportData) -> str:
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

    rec_html = "<br>".join(f"{wc.window_label} - {wc.count}" for wc in data.recebedor_pix_by_window)
    pag_html = "<br>".join(f"{wc.window_label} - {wc.count}" for wc in data.pagador_pix_by_window)

    with_err_html = (
        "<br>".join(f"{s.service} - {fmt_log_val(s.value)} 🔴" for s in data.services_with_errors)
        if data.services_with_errors
        else "Sem erros"
    )
    without_err_html = "<br>".join(
        f"<code>{s.service:<35} {fmt_log_val(s.value):>6} ✅</code>" for s in data.services_without_errors
    )

    latest_rec = data.recebedor_pix_by_window[-1].count if data.recebedor_pix_by_window else 0
    latest_pag = data.pagador_pix_by_window[-1].count if data.pagador_pix_by_window else 0

    all_slots = ["08:30h - 10:30h", "10:30h - 13:30h", "13:30h - 16:30h"]
    slot_rows: list[str] = []
    passed_current = False
    for slot in all_slots:
        if not passed_current:
            badge = period_badge if slot == data.period_label else "✅"
            slot_rows.append(f"<tr><td>{slot}</td><td>{badge}</td><td>0</td><td>Não</td></tr>")
            if slot == data.period_label:
                passed_current = True
        else:
            slot_rows.append(f"<tr><td colspan='4'>{slot}</td></tr>")
    slots_html = "\n".join(slot_rows)

    obs = (
        f"(Observação: Latência do Pagador apresentou P50 em {fmt_duration(pag_p50)} e P95 em {fmt_duration(pag_p95)}. "
        f"No Recebedor, o P50 registrou {fmt_duration(rec_p50)} e o P95 manteve-se em {fmt_duration(rec_p95)}.)"
    )
    comentarios = (
        f"Acompanhamento contínuo. {'Normalização total nos logs' if err_count == 0 else 'Atenção aos logs de erro'}, "
        f"com os {total_services} serviços do SPI analisados. Registrado volume de {fmt_int_br(latest_rec)} transações "
        f"no Recebedor e {fmt_int_br(latest_pag)} no Pagador na janela {data.period_label}, mantendo o acompanhamento "
        "das latências (P50 e P95)."
    )

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Relatório - Observabilidade | Revolut</title>
<style>
body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
    line-height: 1.5;
    color: #111;
}}
table {{ border-collapse: collapse; margin: 10px 0; width: 100%; }}
th, td {{ border: 1px solid #ccc; padding: 6px 10px; text-align: left; }}
th {{ background-color: #f2f2f2; font-weight: bold; }}
code {{ font-family: monospace; white-space: pre; }}
</style>
</head>
<body>
<h2>📊 Relatório - Observabilidade | Revolut</h2>
<p>
📅 <b>Data:</b> {data.date_full}<br>
👤 <b>Responsável:</b> {data.responsavel}<br>
🧩 <b>Aplicação:</b> MIP<br>
🌍 <b>Ambiente:</b> Produção<br>
☁️ <b>Cloud Provider:</b> AWS<br>
⏰ <b>Período:</b> {data.period_label}
</p>
<h3><b>Status Geral do Ambiente</b></h3>
<p>{status_line}</p>
<h3>📌 <b>Eventos Identificados</b></h3>
<p>{eventos_line}</p>
<h3>⚡ <b>Tempos de Processamento PIX</b></h3>
<table>
<thead><tr><th>Métrica</th><th>Pagador</th><th>Recebedor</th></tr></thead>
<tbody>
<tr>
<td><b>P50</b></td>
<td>{fmt_duration(pag_p50)} {pag_p50_badge}</td>
<td>{fmt_duration(rec_p50)} {rec_p50_badge}</td>
</tr>
<tr>
<td><b>P95</b></td>
<td>{fmt_duration(pag_p95)} {pag_p95_badge}</td>
<td>{fmt_duration(rec_p95)} {rec_p95_badge}</td>
</tr>
</tbody>
</table>
<p><i>{obs}</i></p>
<h3>💰 <b>PIXs recebidos Recebedor (aproximado)</b></h3>
<p>{rec_html}</p>
<h3>💰 <b>PIXs recebidos Pagador (aproximado)</b></h3>
<p>{pag_html}</p>
<h3><b>Quantidade de Erros nos Logs (últimos 15m)</b></h3>
<p>🔴 <b>Com Erros:</b><br>{with_err_html}</p>
<p>✅ <b>Sem Erros:</b><br>{without_err_html}</p>
<h3>📊 <b>Resumo:</b></h3>
<p>
<b>Total de serviços analisados:</b> {total_services}<br>
<b>Serviços com erro:</b> {err_count}<br>
<b>Serviços sem erro:</b> {ok_count}
</p>
<h3>🛠️ <b>Comentários Técnicos</b></h3>
<p>{comentarios}</p>
<h3>📞 <b>Chamados Acompanhados</b></h3>
<p>{data.chamados}</p>
<h3>📊 <b>Status por Horário</b></h3>
<table>
<thead><tr><th>Horário</th><th>Status</th><th>Eventos Críticos</th><th>Intervenção Manual</th></tr></thead>
<tbody>
{slots_html}
</tbody>
</table>
<h3>📌 <b>Notas Finais</b></h3>
<p>Nenhum incidente reportado por clientes. A próxima análise está prevista para {data.next_analysis_label}.</p>
</body>
</html>"""
