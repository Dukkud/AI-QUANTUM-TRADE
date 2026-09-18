"""Fail-closed orchestration boundary for VER2.0."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class OrchestrationInputs:
    evidence_ok: bool
    oos_ok: bool
    calibration_ok: bool
    risk_ok: bool
    security_ok: bool
    live_trading: bool

@dataclass(frozen=True)
class OrchestrationResult:
    status: str
    blockers: tuple[str, ...]

def validate_orchestration(x: OrchestrationInputs) -> OrchestrationResult:
    blockers=[]
    if not x.evidence_ok: blockers.append("EVIDENCE_GATE_FAILED")
    if not x.oos_ok: blockers.append("OOS_GATE_FAILED")
    if not x.calibration_ok: blockers.append("CALIBRATION_GATE_FAILED")
    if not x.risk_ok: blockers.append("RISK_GATE_FAILED")
    if not x.security_ok: blockers.append("SECURITY_GATE_FAILED")
    if x.live_trading: blockers.append("LIVE_TRADING_ENABLED")
    return OrchestrationResult("PASS" if not blockers else "BLOCKED", tuple(blockers))
