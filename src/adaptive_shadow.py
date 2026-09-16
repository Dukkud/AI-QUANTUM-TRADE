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
    if not weights or any(v < 0 for v in weights.values()):
        raise ValueError("weights must be non-negative and non-empty")
    total = sum(float(v) for v in weights.values())
    if total <= 0:
        raise ValueError("weight sum must be positive")
    return {k: float(v) / total for k, v in weights.items()}


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
    # Blend normalized performance into current weights, then enforce bounds.
    perf = _normalize(performance_score)
    raw = {k: base[k] * (1 - learning_rate) + perf[k] * learning_rate for k in base}
    bounded = {k: min(max_weight, max(min_weight, v)) for k, v in raw.items()}
    normalized = _normalize(bounded)
    return WeightProposal(proposal_id, base, normalized, "PROPOSED", "shadow proposal only; production weights unchanged")
