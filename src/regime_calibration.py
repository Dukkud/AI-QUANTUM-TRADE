"""Regime-conditioned calibration diagnostics for shadow evidence."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping


@dataclass(frozen=True)
class RegimeCalibration:
    regime: str
    samples: int
    brier_score: float
    ece: float
    status: str


def _ece(confidence: list[float], correct: list[bool], bins: int) -> float:
    total = len(confidence)
    error = 0.0
    for b in range(bins):
        lo = b / bins
        hi = (b + 1) / bins
        idx = [i for i, p in enumerate(confidence) if (lo <= p < hi) or (b == bins - 1 and p == hi)]
        if idx:
            avg_p = sum(confidence[i] for i in idx) / len(idx)
            avg_y = sum(correct[i] for i in idx) / len(idx)
            error += len(idx) / total * abs(avg_p - avg_y)
    return error


def evaluate_regimes(
    observations: Iterable[tuple[str, float, bool]],
    *,
    min_samples: int = 30,
    bins: int = 10,
    max_ece: float = 0.10,
) -> dict[str, RegimeCalibration]:
    if min_samples <= 0 or bins <= 1 or not 0 <= max_ece <= 1:
        raise ValueError("invalid calibration thresholds")
    grouped: dict[str, list[tuple[float, bool]]] = {}
    for regime, confidence, correct in observations:
        if not regime or not 0 <= float(confidence) <= 1:
            raise ValueError("invalid regime observation")
        grouped.setdefault(regime, []).append((float(confidence), bool(correct)))
    out: dict[str, RegimeCalibration] = {}
    for regime, rows in sorted(grouped.items()):
        n = len(rows)
        conf = [x[0] for x in rows]
        corr = [x[1] for x in rows]
        brier = sum((p - float(y)) ** 2 for p, y in rows) / n
        ece = _ece(conf, corr, bins)
        status = "INSUFFICIENT_EVIDENCE" if n < min_samples else ("CALIBRATION_REVIEW" if ece > max_ece else "CALIBRATED_SHADOW")
        out[regime] = RegimeCalibration(regime, n, brier, ece, status)
    return out
