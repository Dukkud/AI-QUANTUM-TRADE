"""Walk-forward stability checks for shadow agent evidence.

The module summarizes already-computed OOS windows. It is not a selector and
never mutates weights, decisions, or execution controls.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from statistics import mean
from typing import Sequence


@dataclass(frozen=True)
class WindowScore:
    samples: int
    accuracy: float
    mean_realized_r: float | None
    max_drawdown_r: float | None


@dataclass(frozen=True)
class StabilityReport:
    status: str
    windows: int
    min_accuracy: float
    max_accuracy: float
    accuracy_std: float
    min_mean_r: float | None
    max_drawdown_r: float | None
    reason: str


def evaluate_stability(
    windows: Sequence[WindowScore],
    *,
    min_samples_per_window: int = 30,
    max_accuracy_std: float = 0.15,
    max_drawdown_r: float = 5.0,
) -> StabilityReport:
    if min_samples_per_window <= 0 or max_accuracy_std < 0 or max_drawdown_r < 0:
        raise ValueError("invalid stability thresholds")
    if not windows:
        return StabilityReport("INSUFFICIENT_EVIDENCE", 0, 0.0, 0.0, 0.0, None, None, "no windows")
    for w in windows:
        if w.samples <= 0 or not 0.0 <= w.accuracy <= 1.0:
            raise ValueError("invalid window score")
        if w.mean_realized_r is not None and not isinstance(w.mean_realized_r, (int, float)):
            raise ValueError("invalid mean_realized_r")
        if w.max_drawdown_r is not None and w.max_drawdown_r < 0:
            raise ValueError("max_drawdown_r must be non-negative")
    if any(w.samples < min_samples_per_window for w in windows):
        return StabilityReport("INSUFFICIENT_EVIDENCE", len(windows), min(w.accuracy for w in windows), max(w.accuracy for w in windows), 0.0, None, max((w.max_drawdown_r or 0.0) for w in windows), f"minimum samples/window={min_samples_per_window}")
    acc = [w.accuracy for w in windows]
    avg = mean(acc)
    std = sqrt(sum((x - avg) ** 2 for x in acc) / len(acc))
    mean_rs = [w.mean_realized_r for w in windows if w.mean_realized_r is not None]
    min_r = min(mean_rs) if mean_rs else None
    max_dd = max((w.max_drawdown_r or 0.0) for w in windows)
    if std > max_accuracy_std:
        return StabilityReport("STABILITY_REVIEW", len(windows), min(acc), max(acc), std, min_r, max_dd, "accuracy dispersion exceeds threshold")
    if max_dd > max_drawdown_r:
        return StabilityReport("STABILITY_REVIEW", len(windows), min(acc), max(acc), std, min_r, max_dd, "drawdown exceeds threshold")
    return StabilityReport("STABLE", len(windows), min(acc), max(acc), std, min_r, max_dd, "all configured stability thresholds satisfied")
