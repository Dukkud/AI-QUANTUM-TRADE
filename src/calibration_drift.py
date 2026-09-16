"""Deterministic shadow calibration/drift checks.

This module compares two already-observed agent metric snapshots. It is
strictly observational: it never changes weights, decisions, models, or
execution controls. Thresholds are explicit inputs so a later policy can be
versioned and audited rather than hidden in the decision engine.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class DriftSnapshot:
    agent: str
    samples: int
    accuracy: float
    brier_score: float
    mean_realized_r: float | None = None
    mean_confidence: float | None = None


@dataclass(frozen=True)
class DriftThresholds:
    min_samples: int = 30
    max_accuracy_drop: float = 0.10
    max_brier_increase: float = 0.05
    max_mean_r_drop: float = 0.50
    max_confidence_shift: float = 0.10


@dataclass(frozen=True)
class DriftResult:
    status: str
    reasons: tuple[str, ...]
    accuracy_delta: float
    brier_delta: float
    mean_realized_r_delta: float | None
    mean_confidence_delta: float | None


def _finite(value: float | None, name: str) -> None:
    if value is not None and not isfinite(value):
        raise ValueError(f"{name} must be finite")


def _validate(snapshot: DriftSnapshot) -> None:
    if not snapshot.agent:
        raise ValueError("agent is required")
    if snapshot.samples < 0:
        raise ValueError("samples must be non-negative")
    if not 0.0 <= snapshot.accuracy <= 1.0 or not isfinite(snapshot.accuracy):
        raise ValueError("accuracy must be finite and within [0, 1]")
    if snapshot.brier_score < 0.0 or not isfinite(snapshot.brier_score):
        raise ValueError("brier_score must be finite and non-negative")
    _finite(snapshot.mean_realized_r, "mean_realized_r")
    _finite(snapshot.mean_confidence, "mean_confidence")
    if snapshot.mean_confidence is not None and not 0.0 <= snapshot.mean_confidence <= 1.0:
        raise ValueError("mean_confidence must be within [0, 1]")


def compare(baseline: DriftSnapshot, current: DriftSnapshot,
            thresholds: DriftThresholds = DriftThresholds()) -> DriftResult:
    """Compare baseline/current observations without mutating either object."""
    _validate(baseline)
    _validate(current)
    if baseline.agent != current.agent:
        raise ValueError("baseline and current agent must match")
    if thresholds.min_samples < 1:
        raise ValueError("min_samples must be positive")

    accuracy_delta = current.accuracy - baseline.accuracy
    brier_delta = current.brier_score - baseline.brier_score
    r_delta = (current.mean_realized_r - baseline.mean_realized_r
               if current.mean_realized_r is not None and baseline.mean_realized_r is not None
               else None)
    confidence_delta = (current.mean_confidence - baseline.mean_confidence
                        if current.mean_confidence is not None and baseline.mean_confidence is not None
                        else None)

    if baseline.samples < thresholds.min_samples or current.samples < thresholds.min_samples:
        return DriftResult("INSUFFICIENT_EVIDENCE", ("minimum sample threshold not met",),
                           accuracy_delta, brier_delta, r_delta, confidence_delta)

    reasons: list[str] = []
    if accuracy_delta < -thresholds.max_accuracy_drop:
        reasons.append("accuracy_drop")
    if brier_delta > thresholds.max_brier_increase:
        reasons.append("brier_increase")
    if r_delta is not None and r_delta < -thresholds.max_mean_r_drop:
        reasons.append("realized_r_drop")
    if confidence_delta is not None and abs(confidence_delta) > thresholds.max_confidence_shift:
        reasons.append("confidence_shift")

    status = "DRIFT_REVIEW" if reasons else "STABLE"
    return DriftResult(status, tuple(reasons), accuracy_delta, brier_delta, r_delta, confidence_delta)
