from app.domain.flagship.models import (
    FlagshipReportData,
    HmlMetrics,
    LogDistribution,
    PodRestart,
    PrdMetrics,
    RdsInstanceCpu,
    RdsMetrics,
)
from app.domain.flagship.status import HealthLevel, evaluate_hml_status, evaluate_prd_status
from app.domain.time_window import WindowCount


def _healthy_report() -> FlagshipReportData:
    return FlagshipReportData(
        date_label="12/11",
        hour_label="10:30h",
        window_label="08:30–10:30",
        hml=HmlMetrics(logs=LogDistribution(total=1000, counts={"INFO": 370, "ERROR": 630})),
        prd=PrdMetrics(
            logs=LogDistribution(total=100000, counts={"INFO": 92500, "WARN": 7400, "ERROR": 100}),
            routing_errors_by_window=[WindowCount("08:30–10:30", 0)],
            api_hits_by_window=[WindowCount("08:30–10:30", 0)],
            lag=2.0,
            saga_total=0,
            saga_above_5m=0,
            polling_processed=1200000,
            polling_total=1,
        ),
        rds=RdsMetrics(instances=[RdsInstanceCpu("transaction-1", 44.421, 50.0, 0)]),
    )


def test_healthy_environments_are_stable() -> None:
    data = _healthy_report()
    prd_st = evaluate_prd_status(data)
    hml_st = evaluate_hml_status(data)
    assert prd_st.level is HealthLevel.STABLE
    assert prd_st.label == "🟢 Estável"
    assert hml_st.level is HealthLevel.STABLE


def test_prd_warning_branches() -> None:
    d1 = _healthy_report()
    d1.chamados_prd = "SOL-00357066"
    assert evaluate_prd_status(d1).level is HealthLevel.WARNING

    d2 = _healthy_report()
    d2.prd.lag = 150.0
    assert evaluate_prd_status(d2).level is HealthLevel.WARNING

    d3 = _healthy_report()
    d3.rds.peaks_above_90 = [RdsInstanceCpu("transaction-1", 60.0, 92.0, points_above_90=1)]
    assert evaluate_prd_status(d3).level is HealthLevel.WARNING

    d4 = _healthy_report()
    d4.prd.restarts = [PodRestart("pod-x", 1.5)]
    assert evaluate_prd_status(d4).level is HealthLevel.WARNING

    d5 = _healthy_report()
    d5.prd.logs = LogDistribution(total=100, counts={"INFO": 70, "WARN": 25, "ERROR": 5})
    assert evaluate_prd_status(d5).level is HealthLevel.WARNING

    d6 = _healthy_report()
    d6.prd.routing_errors_by_window = [WindowCount("08:30–10:30", 10)]
    d6.prd.api_hits_by_window = [WindowCount("08:30–10:30", 10)]
    d6.prd.saga_total = 15
    d6.prd.polling_total = 150
    assert evaluate_prd_status(d6).level is HealthLevel.WARNING

    d7 = _healthy_report()
    d7.prd.saga_total = 2
    assert evaluate_prd_status(d7).level is HealthLevel.STABLE


def test_prd_critical_branches() -> None:
    d1 = _healthy_report()
    d1.prd.restarts = [PodRestart("pod-x", 4.0)]
    assert evaluate_prd_status(d1).level is HealthLevel.CRITICAL

    d2 = _healthy_report()
    d2.rds.peaks_above_90 = [RdsInstanceCpu("transaction-1", 88.0, 95.0, points_above_90=3)]
    assert evaluate_prd_status(d2).level is HealthLevel.CRITICAL

    d3 = _healthy_report()
    d3.prd.lag = 1500.0
    assert evaluate_prd_status(d3).level is HealthLevel.CRITICAL

    d4 = _healthy_report()
    d4.prd.saga_above_5m = 2
    assert evaluate_prd_status(d4).level is HealthLevel.CRITICAL

    d5 = _healthy_report()
    d5.prd.logs = LogDistribution(total=100, counts={"INFO": 40, "ERROR": 60})
    d5.prd.polling_total = 10000
    assert evaluate_prd_status(d5).level is HealthLevel.CRITICAL


def test_hml_warning_and_critical_branches() -> None:
    d0 = _healthy_report()
    d0.hml.lag = 5.0
    assert evaluate_hml_status(d0).level is HealthLevel.STABLE

    d1 = _healthy_report()
    d1.hml.lag = 50.0
    d1.chamados_hml = "INC-1"
    assert evaluate_hml_status(d1).level is HealthLevel.WARNING

    d2 = _healthy_report()
    d2.hml.lag = 1500.0
    d2.hml.restarts = [PodRestart("pod-h", 4.0)]
    assert evaluate_hml_status(d2).level is HealthLevel.CRITICAL
