"""Canonical status model for AI-QUANTUM hourly audits.

The key safety rule is that missing telemetry is not a failed trading result.
Performance state and execution authorization are independent dimensions.
"""
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Mapping


class PerformanceStatus(str, Enum):
    PROMOTE = "PROMOTE"
    HOLD = "HOLD"
    DEGRADE = "DEGRADE"
    QUARANTINE = "QUARANTINE"
    UNVERIFIED = "UNVERIFIED"


class AgentStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class RiskStatus(str, Enum):
    ENABLED = "ENABLED"
    DEGRADED = "DEGRADED"
    QUARANTINED = "QUARANTINED"
    UNVERIFIED = "UNVERIFIED"


class ExecutionGate(str, Enum):
    PAPER = "PAPER"
    SHADOW = "SHADOW"
    LIVE_BLOCKED = "LIVE_BLOCKED"
    LIVE_ELIGIBLE = "LIVE_ELIGIBLE"
    LIVE = "LIVE"


@dataclass(frozen=True)
class AgentStatusRecord:
    agent: str
    agent_status: AgentStatus
    performance_status: PerformanceStatus
    risk_status: RiskStatus
    execution_gate: ExecutionGate
    telemetry_verified: bool
    reason: str

    def to_dict(self) -> dict:
        return {k: (v.value if isinstance(v, Enum) else v) for k, v in asdict(self).items()}


def classify_performance(*, telemetry_verified: bool, degraded: bool = False,
                         quarantined: bool = False, promotable: bool = False) -> PerformanceStatus:
    """Fail closed for performance claims, without treating missing data as failure."""
    if quarantined:
        return PerformanceStatus.QUARANTINE
    if degraded:
        return PerformanceStatus.DEGRADE
    if promotable:
        return PerformanceStatus.PROMOTE
    if not telemetry_verified:
        return PerformanceStatus.UNVERIFIED
    return PerformanceStatus.HOLD


def build_agent_status(agent: str, *, active: bool = True,
                       telemetry_verified: bool = False, degraded: bool = False,
                       quarantined: bool = False, promotable: bool = False,
                       risk_status: RiskStatus = RiskStatus.UNVERIFIED,
                       execution_gate: ExecutionGate = ExecutionGate.PAPER) -> AgentStatusRecord:
    performance = classify_performance(
        telemetry_verified=telemetry_verified,
        degraded=degraded,
        quarantined=quarantined,
        promotable=promotable,
    )
    if quarantined:
        risk_status = RiskStatus.QUARANTINED
    return AgentStatusRecord(
        agent=agent,
        agent_status=AgentStatus.ACTIVE if active else AgentStatus.INACTIVE,
        performance_status=performance,
        risk_status=risk_status,
        execution_gate=execution_gate,
        telemetry_verified=telemetry_verified,
        reason=("validated performance evidence" if promotable else
                "validated degradation" if degraded else
                "risk quarantine triggered" if quarantined else
                "telemetry evidence not yet sufficient" if not telemetry_verified else
                "validated telemetry; insufficient evidence for promotion"),
    )


def build_all_agent_status(agents: Mapping[str, object]) -> dict[str, dict]:
    """Produce the canonical Q1-Q8 status table from the paper-world/adaptive state."""
    result = {}
    for agent, obj in agents.items():
        active = bool(getattr(obj, "active", True))
        locked = bool(getattr(obj, "locked_until", None))
        result[agent] = build_agent_status(
            agent,
            active=active,
            telemetry_verified=False,
            quarantined=locked,
            risk_status=RiskStatus.QUARANTINED if locked else RiskStatus.UNVERIFIED,
            execution_gate=ExecutionGate.LIVE_BLOCKED,
        ).to_dict()
    return result
