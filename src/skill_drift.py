from __future__ import annotations
from dataclasses import dataclass
import math

@dataclass(frozen=True)
class DriftResult:
    status: str
    delta: float
    reason: str

def detect_drift(baseline_brier: float, current_brier: float, max_degradation: float = 0.05) -> DriftResult:
    if not all(math.isfinite(x) for x in (baseline_brier,current_brier,max_degradation)) or baseline_brier < 0 or current_brier < 0 or max_degradation < 0:
        raise ValueError("invalid drift inputs")
    delta=current_brier-baseline_brier
    drift=delta > max_degradation
    return DriftResult("DRIFT" if drift else "STABLE", delta, "Brier degradation exceeds threshold" if drift else "Within threshold")
