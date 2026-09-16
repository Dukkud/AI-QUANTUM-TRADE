"""Locked-OOS champion/challenger comparison for shadow experiments."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class LockedExperiment:
    dataset_id: str
    dataset_sha256: str
    samples: int
    baseline_mean_r: float
    challenger_mean_r: float
    delta_mean_r: float
    baseline_accuracy: float
    challenger_accuracy: float
    status: str
    reason: str


def compare_locked_oos(
    *,
    dataset_id: str,
    dataset_sha256: str,
    baseline_r: Sequence[float],
    challenger_r: Sequence[float],
    baseline_correct: Sequence[bool],
    challenger_correct: Sequence[bool],
    min_samples: int = 30,
) -> LockedExperiment:
    if not dataset_id or not dataset_sha256:
        raise ValueError("locked dataset identity is required")
    if len(baseline_r) != len(challenger_r) or len(baseline_r) != len(baseline_correct) or len(baseline_r) != len(challenger_correct):
        raise ValueError("paired OOS arrays must have equal length")
    n = len(baseline_r)
    if n < min_samples:
        return LockedExperiment(dataset_id, dataset_sha256, n, 0.0, 0.0, 0.0, 0.0, 0.0, "INSUFFICIENT_EVIDENCE", f"minimum samples={min_samples}")
    b_r = sum(float(x) for x in baseline_r) / n
    c_r = sum(float(x) for x in challenger_r) / n
    b_a = sum(bool(x) for x in baseline_correct) / n
    c_a = sum(bool(x) for x in challenger_correct) / n
    return LockedExperiment(dataset_id, dataset_sha256, n, b_r, c_r, c_r - b_r, b_a, c_a, "OBSERVE", "paired locked-OOS comparison only")
