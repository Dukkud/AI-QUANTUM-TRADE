"""Training journal that teaches agents the difference between paper and live execution."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class LatencyObservation:
    feed_latency_ms: Optional[int]
    decision_latency_ms: Optional[int]
    simulated_execution_latency_ms: int
    slippage_bps: float
    source: str
    training_only: bool = True


class TrainingJournal:
    """Stores execution assumptions separately from market observations."""

    def __init__(self) -> None:
        self.observations: list[LatencyObservation] = []

    def record(self, observation: LatencyObservation) -> None:
        self.observations.append(observation)

    def summary(self) -> dict:
        if not self.observations:
            return {"count": 0, "training_only": True}
        lat = [x.feed_latency_ms for x in self.observations if x.feed_latency_ms is not None]
        slip = [x.slippage_bps for x in self.observations]
        return {
            "count": len(self.observations),
            "avg_feed_latency_ms": sum(lat) / len(lat) if lat else None,
            "max_feed_latency_ms": max(lat) if lat else None,
            "avg_slippage_bps": sum(slip) / len(slip),
            "training_only": True,
            "live_latency_not_guaranteed": True,
        }

    def export(self) -> list[dict]:
        return [asdict(x) for x in self.observations]
