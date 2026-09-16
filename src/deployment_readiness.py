"""Deployment-readiness gate for research-to-paper promotion.

This gate verifies evidence prerequisites only. It cannot enable live execution.
"""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ReadinessInputs:
    source_validated: bool
    provenance_complete: bool
    reconciliation_passed: bool
    oos_stable: bool
    paper_forward_validated: bool
    secrets_configured: bool
    live_execution_enabled: bool = False

@dataclass(frozen=True)
class ReadinessResult:
    status: str
    blockers: tuple[str, ...]

def evaluate_readiness(x: ReadinessInputs) -> ReadinessResult:
    blockers = []
    for field, label in (
        (x.source_validated, "SOURCE_VALIDATION"),
        (x.provenance_complete, "PROVENANCE"),
        (x.reconciliation_passed, "RECONCILIATION"),
        (x.oos_stable, "OOS_STABILITY"),
        (x.paper_forward_validated, "FORWARD_PAPER"),
        (x.secrets_configured, "SECRETS_CONFIGURATION"),
    ):
        if not field:
            blockers.append(label)
    if x.live_execution_enabled:
        blockers.append("LIVE_EXECUTION_MUST_REMAIN_EXTERNAL_AND_FAIL_CLOSED")
    return ReadinessResult("READY_FOR_PAPER_PROMOTION" if not blockers else "BLOCKED", tuple(blockers))
