"""Fail-closed Q9 self-learning control plane.

Q9 may coordinate shadow-learning experiments and proposals, but cannot mutate
production weights, bypass evidence/OOS/calibration gates, or enable live trading.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Q9Decision:
    status: str
    reason: str


def evaluate_q9(*, evidence_ok: bool, oos_ok: bool, calibration_ok: bool,
                production_mutation_requested: bool, live_trading_requested: bool) -> Q9Decision:
    if production_mutation_requested:
        return Q9Decision("BLOCKED", "PRODUCTION_MUTATION_NOT_AUTHORIZED")
    if live_trading_requested:
        return Q9Decision("BLOCKED", "LIVE_TRADING_NOT_AUTHORIZED")
    if not evidence_ok:
        return Q9Decision("BLOCKED", "EVIDENCE_GATE_FAILED")
    if not oos_ok:
        return Q9Decision("BLOCKED", "OOS_GATE_FAILED")
    if not calibration_ok:
        return Q9Decision("BLOCKED", "CALIBRATION_GATE_FAILED")
    return Q9Decision("SHADOW_LEARNING", "ELIGIBLE_FOR_SHADOW_EXPERIMENT")
