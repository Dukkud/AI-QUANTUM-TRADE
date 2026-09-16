"""Evidence event contracts kept outside the agent/ML decision path.

These records provide a stable join key (prediction_id) for linking an AI
prediction to later broker/execution observations. They do not place orders or
modify agent weights.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PredictionEvent:
    prediction_id: str
    observed_at_utc: str
    asset: str
    timeframe: str
    decision: str
    direction: str | None
    entry: float | None
    stop: float | None
    target: float | None
    confidence: float | None
    agent_outputs: dict[str, Any]


@dataclass(frozen=True)
class OutcomeEvent:
    prediction_id: str
    observed_at_utc: str
    status: str
    exit_price: float | None = None
    realized_r: float | None = None
    slippage: float | None = None
    commission: float | None = None
    holding_seconds: int | None = None
    mfe_r: float | None = None
    mae_r: float | None = None
    source: str = "wundertrading"


def validate_link(prediction: PredictionEvent, outcome: OutcomeEvent) -> bool:
    """Return True only when an outcome belongs to the same prediction."""
    return bool(prediction.prediction_id) and prediction.prediction_id == outcome.prediction_id


def agent_realized_contribution(agent_output: Any, realized_r: float | None) -> float | None:
    """Convert a realized trade result into an auditable signed contribution.

    This is intentionally descriptive only. It does not update weights or
    retrain models. Attribution rules can be upgraded after sufficient evidence
    is accumulated and validated.
    """
    if realized_r is None or not isinstance(agent_output, dict):
        return None
    confidence = agent_output.get("confidence")
    if not isinstance(confidence, (int, float)):
        return None
    confidence = max(0.0, min(1.0, float(confidence)))
    return float(realized_r) * confidence
