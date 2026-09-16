"""Locked out-of-sample challenger comparison.

Evaluation-only: compares immutable challenger metrics on a sealed OOS set.
It never mutates production weights or execution state.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence


@dataclass(frozen=True)
class ChallengerMetrics:
    model_id: str
    samples: int
    mean_realized_r: float
    accuracy: float
    brier_score: float


@dataclass(frozen=True)
class ChallengerResult:
    challenger_id: str
    baseline_id: str
    status: str
    delta_mean_r: float
    delta_accuracy: float
    delta_brier: float


def compare_locked_oos(
    baseline: ChallengerMetrics,
    challenger: ChallengerMetrics,
    *,
    min_samples: int = 100,
    min_delta_r: float = 0.0,
    max_brier_worsening: float = 0.0,
) -> ChallengerResult:
    if baseline.samples != challenger.samples or baseline.samples < min_samples:
        raise ValueError("locked OOS samples must match and meet minimum")
    if baseline.model_id == challenger.model_id:
        raise ValueError("baseline and challenger must differ")
    values = (baseline.mean_realized_r, challenger.mean_realized_r,
              baseline.accuracy, challenger.accuracy,
              baseline.brier_score, challenger.brier_score)
    if not all(isfinite(float(v)) for v in values):
        raise ValueError("non-finite OOS metric")
    dr = challenger.mean_realized_r - baseline.mean_realized_r
    da = challenger.accuracy - baseline.accuracy
    db = challenger.brier_score - baseline.brier_score
    status = "PASS" if dr >= min_delta_r and db <= max_brier_worsening else "REVIEW"
    return ChallengerResult(challenger.model_id, baseline.model_id, status, dr, da, db)
