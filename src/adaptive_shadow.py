"""Shadow-only adaptive weight proposal engine.

Produces a versioned proposal from validated evidence. It never mutates the
production weight map and cannot enable live execution.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class WeightProposal:
    proposal_id: str
    base_weights: dict[str, float]
    proposed_weights: dict[str, float]
    status: str
    reason: str


def _normalize(weights: Mapping[str, float]) -> dict[str, float]:
    if not weights or any(float(v) < 0 for v in weights.values()):
        raise ValueError("weights must be non-negative and non-empty")
    total = sum(float(v) for v in weights.values())
    if total <= 0:
        raise ValueError("weight sum must be positive")
    return {k: float(v) / total for k, v in weights.items()}


def _bounded_normalize(weights: Mapping[str, float], low: float, high: float) -> dict[str, float]:
    if len(weights) * low > 1 or len(weights) * high < 1:
        raise ValueError("weight bounds cannot contain a unit-sum distribution")
    values = _normalize(weights)
    fixed: dict[str, float] = {}
    free = set(values)
    remaining = 1.0
    while free:
        denominator = sum(values[j] for j in free)
        proposed = {k: values[k] * remaining / denominator for k in free}
        changed = False
        for k, v in list(proposed.items()):
            if v < low:
                fixed[k] = low
                remaining -= low
                free.remove(k)
                changed = True
            elif v > high:
                fixed[k] = high
                remaining -= high
                free.remove(k)
                changed = True
        if not changed:
            fixed.update(proposed)
            break
        if remaining < -1e-12:
            raise ValueError("weight bounds infeasible")
    if abs(sum(fixed.values()) - 1.0) > 1e-9:
        raise ValueError("bounded normalization failed")
    return fixed


def propose_weights(
    current: Mapping[str, float],
    performance_score: Mapping[str, float],
    *,
    evidence_ready: bool,
    stability_status: str,
    learning_rate: float = 0.10,
    min_weight: float = 0.02,
    max_weight: float = 0.30,
    proposal_id: str = "shadow-proposal-v1",
) -> WeightProposal:
    if not 0 < learning_rate <= 1 or not 0 <= min_weight <= max_weight <= 1:
        raise ValueError("invalid adaptation bounds")
    base = _normalize(current)
    if set(base) != set(performance_score) or any(not 0 <= float(v) <= 1 for v in performance_score.values()):
        raise ValueError("performance scores must match agents and be within [0,1]")
    if not evidence_ready or stability_status != "STABLE":
        return WeightProposal(proposal_id, base, base, "HOLD", "evidence or stability gate not satisfied")
    perf = _normalize(performance_score)
    raw = {k: base[k] * (1 - learning_rate) + perf[k] * learning_rate for k in base}
    proposed = _bounded_normalize(raw, min_weight, max_weight)
    return WeightProposal(proposal_id, base, proposed, "PROPOSED", "shadow proposal only; production weights unchanged")
