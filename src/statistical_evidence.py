"""Statistical evidence gates for shadow agent evaluation.

Descriptive/statistical layer only. It does not change model weights, trading
decisions, or execution state.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from random import Random
from statistics import mean
from typing import Sequence


@dataclass(frozen=True)
class ConfidenceInterval:
    lower: float
    upper: float


@dataclass(frozen=True)
class StatisticalGate:
    status: str
    samples: int
    accuracy_ci: ConfidenceInterval
    mean_r_ci: ConfidenceInterval | None
    reason: str


def wilson_interval(correct: int, samples: int, z: float = 1.96) -> ConfidenceInterval:
    if samples <= 0 or correct < 0 or correct > samples or z <= 0:
        raise ValueError("invalid binomial inputs")
    p = correct / samples
    denom = 1.0 + z * z / samples
    centre = (p + z * z / (2 * samples)) / denom
    radius = z * sqrt((p * (1 - p) / samples) + (z * z / (4 * samples * samples))) / denom
    return ConfidenceInterval(max(0.0, centre - radius), min(1.0, centre + radius))


def bootstrap_mean_interval(values: Sequence[float], *, iterations: int = 2000, seed: int = 42, alpha: float = 0.05) -> ConfidenceInterval:
    if not values or iterations < 100 or not 0 < alpha < 1:
        raise ValueError("invalid bootstrap inputs")
    if any(not isinstance(x, (int, float)) for x in values):
        raise ValueError("values must be numeric")
    rng = Random(seed)
    n = len(values)
    samples = sorted(mean(values[rng.randrange(n)] for _ in range(n)) for _ in range(iterations))
    lo = samples[int((alpha / 2) * iterations)]
    hi = samples[min(iterations - 1, int((1 - alpha / 2) * iterations))]
    return ConfidenceInterval(float(lo), float(hi))


def evaluate(correct: Sequence[bool], realized_r: Sequence[float] | None = None, *, min_samples: int = 30) -> StatisticalGate:
    if min_samples <= 0:
        raise ValueError("min_samples must be positive")
    n = len(correct)
    if n == 0:
        return StatisticalGate("INSUFFICIENT_EVIDENCE", 0, ConfidenceInterval(0.0, 0.0), None, "no observations")
    if n < min_samples:
        ci = wilson_interval(sum(correct), n)
        return StatisticalGate("INSUFFICIENT_EVIDENCE", n, ci, None, f"minimum samples={min_samples}")
    if realized_r is not None and len(realized_r) != n:
        raise ValueError("realized_r length must match correct")
    acc_ci = wilson_interval(sum(correct), n)
    r_ci = bootstrap_mean_interval(realized_r) if realized_r is not None else None
    return StatisticalGate("EVIDENCE_READY", n, acc_ci, r_ci, "minimum evidence satisfied")
