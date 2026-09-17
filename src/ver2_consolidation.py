"""VER2.0 consolidation readiness checks.

This module verifies architectural completeness without authorizing execution.
"""
from __future__ import annotations

from dataclasses import dataclass
from .agent_registry import validate_agent_registry


@dataclass(frozen=True)
class ConsolidationResult:
    status: str
    blockers: tuple[str, ...]


REQUIRED_CONTROL_LAYERS = (
    "evidence",
    "lineage",
    "rolling_oos",
    "calibration",
    "risk",
    "security",
    "recovery",
    "skills",
    "qgraph",
    "workgraph",
    "workmachine",
)


def validate_consolidation(*, controls_present: set[str], live_trading: bool) -> ConsolidationResult:
    blockers = list(validate_agent_registry())
    blockers.extend(
        f"MISSING_CONTROL_LAYER:{name}"
        for name in REQUIRED_CONTROL_LAYERS
        if name not in controls_present
    )
    if live_trading:
        blockers.append("LIVE_TRADING_ENABLED")
    return ConsolidationResult("PASS" if not blockers else "BLOCKED", tuple(blockers))
