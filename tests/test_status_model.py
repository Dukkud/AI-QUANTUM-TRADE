from src.status_model import (
    ExecutionGate,
    PerformanceStatus,
    RiskStatus,
    build_agent_status,
    classify_performance,
)


def test_missing_telemetry_is_unverified_not_hold_or_degrade():
    assert classify_performance(telemetry_verified=False) == PerformanceStatus.UNVERIFIED


def test_verified_without_promotion_is_hold():
    assert classify_performance(telemetry_verified=True) == PerformanceStatus.HOLD


def test_degrade_requires_positive_evidence():
    assert classify_performance(telemetry_verified=True, degraded=True) == PerformanceStatus.DEGRADE


def test_quarantine_overrides_other_performance_states():
    assert classify_performance(telemetry_verified=True, promotable=True, quarantined=True) == PerformanceStatus.QUARANTINE


def test_paper_status_does_not_authorize_live_execution():
    record = build_agent_status("Q8", telemetry_verified=False, risk_status=RiskStatus.ENABLED)
    assert record.performance_status == PerformanceStatus.UNVERIFIED
    assert record.execution_gate == ExecutionGate.PAPER


def test_q8_quarantine_sets_risk_quarantined():
    record = build_agent_status("Q8", quarantined=True)
    assert record.performance_status == PerformanceStatus.QUARANTINE
    assert record.risk_status == RiskStatus.QUARANTINED
