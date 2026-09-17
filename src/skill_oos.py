from __future__ import annotations
from dataclasses import dataclass
import math

@dataclass(frozen=True)
class SkillOOSResult:
    status: str
    samples: int
    net_r: float
    brier: float

def evaluate_skill_oos(realized_r, brier: float, min_samples: int = 30, min_net_r: float = 0.0, max_brier: float = 0.25) -> SkillOOSResult:
    if min_samples < 1:
        raise ValueError("min_samples")
    n = len(realized_r)
    if n < min_samples:
        return SkillOOSResult("INSUFFICIENT_EVIDENCE", n, float(sum(realized_r)), brier)
    if not all(math.isfinite(x) for x in realized_r):
        raise ValueError("non-finite realized_r")
    if not math.isfinite(brier) or not 0 <= brier <= 1:
        raise ValueError("invalid brier")
    net = float(sum(realized_r))
    status = "PASS_SHADOW" if net >= min_net_r and brier <= max_brier else "FAIL_SHADOW"
    return SkillOOSResult(status, n, net, brier)
