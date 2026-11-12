from app.domain.flagship.formatter import fmt_int, fmt_num, format_flagship_report
from app.domain.flagship.models import (
    FlagshipReportData,
    HmlMetrics,
    LogDistribution,
    PodRestart,
    PrdMetrics,
    RdsInstanceCpu,
    RdsMetrics,
)
from app.domain.time_window import WindowCount


def test_fmt_helpers() -> None:
    assert fmt_int(None) == "No Data"
    assert fmt_num(None) == "No Data"
    assert fmt_num(14.2) == "14.2"


def test_format_report_matches_template() -> None:
    data = FlagshipReportData(
        date_label="11/11",
        hour_label="16:30h",
        window_label="13:30–16:30",
        hml=HmlMetrics(
            logs=LogDistribution(total=10000, counts={"INFO": 4447, "WARN": 7, "ERROR": 5540, "DEBUG": 6}),
            incidents=None,
            lag=None,
            restarts=[PodRestart(pod="cc-integ-acc-ev-consumer-instvld", restarts=2.96)],
        ),
        prd=PrdMetrics(
            logs=LogDistribution(total=9122000, counts={"INFO": 8392240, "WARN": 690535, "ERROR": 4561}),
            routing_errors_by_window=[
                WindowCount("08:30–10:30", 0),
                WindowCount("10:30–13:30", 1),
                WindowCount("13:30–16:30", 2),
            ],
            incidents=14.2,
            lag=None,
            restarts=[],
            saga_total=0,
            saga_above_5m=0,
            polling_processed=1217407,
            polling_total=3,
            api_hits_by_window=[
                WindowCount("08:30–10:30", 0),
                WindowCount("10:30–13:30", 0),
                WindowCount("13:30–16:30", 0),
            ],
        ),
        rds=RdsMetrics(
            peaks_above_90=[],
            instances=[
                RdsInstanceCpu("transaction-1", 44.703),
                RdsInstanceCpu("conciliation-1", None),
            ],
        ),
    )

    rendered = format_flagship_report(data)
    assert "📊 RELATÓRIO DTW — 11/11 às 16:30h" in rendered
    assert "🔴 ERROR: 0.05% (4.561)" in rendered
    assert "Registros PROCESSED: 1.217.407 🟢" in rendered
    assert "Incidentes (últimas 5h): No Data" in rendered
    assert "Restarts de pods (últimas 6h):" in rendered
    assert "Incidentes (últimos 30 min): 14.2 🟢" in rendered
    assert "conciliation-1: No Data" in rendered
    assert "Produção (PRD): 🟢 Estável" in rendered
    assert "Homologação (HML): 🟡 Atenção" in rendered


def test_format_report_variants() -> None:
    data = FlagshipReportData(
        date_label="12/11",
        hour_label="10:30h",
        window_label="08:30–10:30",
        prd=PrdMetrics(lag=1200.0, polling_total=12000, saga_total=15, saga_above_5m=1),
        rds=RdsMetrics(
            peaks_above_90=[
                RdsInstanceCpu("db-1", 80.0, 92.0, points_above_90=1),
                RdsInstanceCpu("db-2", 95.0, 96.0, points_above_90=3),
            ],
            instances=[],
        ),
    )
    rendered = format_flagship_report(data)
    assert "1.200 🔴" in rendered
    assert "db-1: 92.000% 🟡" in rendered
    assert "db-2: 96.000% 🔴" in rendered
    assert "Total de integrações: 15 🟡" in rendered
    assert "Integrações acima de 5 min: 1 🔴" in rendered
    assert "Sem dados disponíveis" in rendered

    data_err = FlagshipReportData(
        date_label="12/11",
        hour_label="10:30h",
        window_label="08:30–10:30",
        prd=PrdMetrics(lag=50.0, polling_total=200),
        rds=RdsMetrics(error="Falha RDS"),
    )
    rendered_err = format_flagship_report(data_err)
    assert "Erro na coleta: Falha RDS" in rendered_err
    assert "50 🟡" in rendered_err
