"""Shadow-learning validation for agent predictions.

This module measures calibration and realized outcomes without changing agent
weights, decisions, or execution controls. It is intentionally safe to run
alongside live model training.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Iterable


@dataclass(frozen=True)
class LearningObservation:
    agent: str
    confidence: float
    correct: bool
    realized_r: float | None = None


@dataclass(frozen=True)
class AgentLearningMetrics:
    samples: int
    accuracy: float
    brier_score: float
    mean_realized_r: float | None
    win_rate: float | None
    max_drawdown_r: float | None


def _validate(observation: LearningObservation) -> None:
    if not observation.agent:
        raise ValueError("agent is required")
    if not isfinite(observation.confidence) or not 0.0 <= observation.confidence <= 1.0:
        raise ValueError("confidence must be finite and within [0, 1]")
    if observation.realized_r is not None and not isfinite(observation.realized_r):
        raise ValueError("realized_r must be finite")


def evaluate(observations: Iterable[LearningObservation]) -> dict[str, AgentLearningMetrics]:
    grouped: dict[str, list[LearningObservation]] = {}
    for item in observations:
        _validate(item)
        grouped.setdefault(item.agent, []).append(item)

    result: dict[str, AgentLearningMetrics] = {}
    for agent, items in grouped.items():
        n = len(items)
        accuracy = sum(item.correct for item in items) / n
        brier = sum((item.confidence - float(item.correct)) ** 2 for item in items) / n
        realized = [item.realized_r for item in items if item.realized_r is not None]
        wins = [r for r in realized if r > 0]
        mean_r = sum(realized) / len(realized) if realized else None
        win_rate = len(wins) / len(realized) if realized else None

        peak = 0.0
        equity = 0.0
        max_dd = 0.0
        for r in realized:
            equity += r
            peak = max(peak, equity)
            max_dd = max(max_dd, peak - equity)

        result[agent] = AgentLearningMetrics(
            samples=n,
            accuracy=accuracy,
            brier_score=brier,
            mean_realized_r=mean_r,
            win_rate=win_rate,
            max_drawdown_r=max_dd,
        )
    return result


def learning_gate(metrics: AgentLearningMetrics, *, min_samples: int = 30,
                  max_brier: float = 0.25) -> str:
    """Return a descriptive gate; never mutates weights or enables trading."""
    if metrics.samples < min_samples:
        return "INSUFFICIENT_EVIDENCE"
    if metrics.brier_score > max_brier:
        return "CALIBRATION_REVIEW"
    return "OBSERVE"
