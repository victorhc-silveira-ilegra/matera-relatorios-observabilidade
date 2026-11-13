from app.domain.revolut.formatter import fmt_duration, format_revolut_report, latency_badge
from app.domain.revolut.models import (
    RevolutLatency,
    RevolutReportData,
    RevolutServiceError,
)
from app.domain.time_window import WindowCount


def test_revolut_helpers() -> None:
    assert fmt_duration(None) == "No Data"
    assert fmt_duration(0.5) == "500ms"
    assert latency_badge(None, 1.0) == "⚠️"
    assert latency_badge(1.1, 1.0) == "🟡"
    assert latency_badge(1.5, 1.0) == "🔴"


def test_format_revolut_report_healthy() -> None:
    data = RevolutReportData(
        date_full="11/11/2026",
        period_label="13:30h - 16:30h",
        current_window_label="13:30–16:30",
        responsavel="Victor Silveira",
        pagador_latency=RevolutLatency(p50_seconds=0.25418, p95_seconds=0.63365),
        recebedor_latency=RevolutLatency(p50_seconds=0.9115, p95_seconds=1.375),
        recebedor_pix_by_window=[
            WindowCount("08:30 à 10:30", 7338),
            WindowCount("10:30 à 13:30", 13265),
            WindowCount("13:30 à 16:30", 12613),
        ],
        pagador_pix_by_window=[
            WindowCount("08:30 à 10:30", 10414),
            WindowCount("10:30 à 13:30", 19088),
            WindowCount("13:30 à 16:30", 18775),
        ],
        services_with_errors=[],
        services_without_errors=[
            RevolutServiceError("spi-addressing", 51.9),
            RevolutServiceError("spi-main", 0.0),
        ],
        chamados="Sem ocorrências.",
        next_analysis_label="11/11/2026 às 16:30h",
    )

    rendered = format_revolut_report(data)
    assert "📊 Relatório - Observabilidade | Revolut" in rendered
    assert "Ambiente estável ✅" in rendered
    assert "254.18ms ✅" in rendered
    assert "1.375s ✅" in rendered


def test_format_revolut_report_warning_and_critical() -> None:
    warn_data = RevolutReportData(
        date_full="12/11/2026",
        period_label="08:30h - 10:30h",
        current_window_label="08:30–10:30",
        pagador_latency=RevolutLatency(p50_seconds=0.5, p95_seconds=1.0),
        recebedor_latency=RevolutLatency(p50_seconds=0.9, p95_seconds=1.4),
        services_without_errors=[
            RevolutServiceError("spi-addressing-queues", 2.67),
            RevolutServiceError("spi-main", 15.0),
        ],
        chamados="SOL-123 em analise",
        next_analysis_label="12/11/2026 às 13:30h",
    )
    rendered_warn = format_revolut_report(warn_data)
    assert "Ambiente em atenção 🟡" in rendered_warn
    assert "spi-addressing-queues" in rendered_warn

    service_warn_data = RevolutReportData(
        date_full="13/11/2026",
        period_label="13:30h - 16:30h",
        current_window_label="13:30–16:30",
        pagador_latency=RevolutLatency(p50_seconds=0.25, p95_seconds=0.63),
        recebedor_latency=RevolutLatency(p50_seconds=0.88, p95_seconds=1.44),
        services_with_errors=[RevolutServiceError("spi-dispute", 223.7)],
        services_without_errors=[RevolutServiceError("spi-main", 26.4)],
        chamados="Sem ocorrências.",
        next_analysis_label="16/11/2026 às 10:30h",
    )
    rendered_service_warn = format_revolut_report(service_warn_data)
    assert "Ambiente em atenção 🟡" in rendered_service_warn
    assert "Identificados 1 serviço(s) com erros nos logs em acompanhamento contínuo." in rendered_service_warn
    assert "13:30h - 16:30h  🟡         0                   Não" in rendered_service_warn

    crit_data = RevolutReportData(
        date_full="12/11/2026",
        period_label="08:30h - 10:30h",
        current_window_label="08:30–10:30",
        pagador_latency=RevolutLatency(p50_seconds=1.5, p95_seconds=2.5),
        recebedor_latency=RevolutLatency(p50_seconds=0.9, p95_seconds=1.4),
        services_with_errors=[
            RevolutServiceError("spi-main", 250.0),
            RevolutServiceError("spi-dispute", 120.0),
        ],
        next_analysis_label="12/11/2026 às 13:30h",
    )
    rendered_crit = format_revolut_report(crit_data)
    assert "Ambiente instável 🔴" in rendered_crit
    assert "spi-main - 250.0 🔴" in rendered_crit
    assert "spi-dispute - 120.0 🔴" in rendered_crit
