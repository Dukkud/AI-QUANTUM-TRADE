"""Sequential-look and multiple-comparison controls for shadow evidence."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SequentialLook:
    look: int
    alpha_spent: float


def alpha_spending(look: int, total_looks: int, alpha: float = 0.05) -> SequentialLook:
    if look <= 0 or total_looks <= 0 or look > total_looks or not 0 < alpha < 1:
        raise ValueError("invalid sequential-testing inputs")
    # Conservative linear alpha spending: cumulative alpha = alpha * look / total_looks.
    return SequentialLook(look, alpha * look / total_looks)


def holm_bonferroni(p_values: list[float], alpha: float = 0.05) -> list[bool]:
    if not p_values or not 0 < alpha < 1 or any(not 0 <= p <= 1 for p in p_values):
        raise ValueError("invalid p-values")
    ordered = sorted(enumerate(p_values), key=lambda x: x[1])
    decisions = [False] * len(p_values)
    for rank, (index, p_value) in enumerate(ordered):
        threshold = alpha / (len(p_values) - rank)
        if p_value <= threshold:
            decisions[index] = True
        else:
            break
    return decisions
