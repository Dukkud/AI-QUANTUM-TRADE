"""Research adapter for andyluu98/midas-agent.

Midas is used as an architectural donor: specialist council/debate, multi-TF
forecasting, external news/sentiment and memory concepts. Its broker execution,
credentials, model endpoints and position-sizing assumptions are deliberately
not imported into AI-QUANTUM.
"""

from dataclasses import dataclass
from typing import Mapping

SOURCE_REPO = "andyluu98/midas-agent"
SOURCE_LICENSE = "Apache-2.0"

SPECIALISTS = (
    "fundamentals",
    "sentiment",
    "news",
    "technical",
)
RISK_ROLES = ("risk_debator_1", "risk_debator_2", "risk_debator_3")
FORECAST_TIMEFRAMES = ("H1", "M15", "M5")

@dataclass(frozen=True)
class CouncilOpinion:
    specialist: str
    direction: str
    confidence: float
    rationale: str


def council_contract() -> dict[str, object]:
    """Return the safe interface contract for a Midas-inspired council."""
    return {
        "specialists": list(SPECIALISTS),
        "risk_roles": list(RISK_ROLES),
        "forecast_timeframes": list(FORECAST_TIMEFRAMES),
        "output": ["BUY", "SELL", "WAIT"],
        "execution": "DISABLED",
        "human_approval": True,
        "memory": "research_only",
    }


def aggregate(opinions: Mapping[str, CouncilOpinion]) -> dict[str, object]:
    """Aggregate specialist opinions without majority-vote execution.

    The result is an input to QuantumCore. A tie or weak confidence becomes
    WAIT; no broker action is possible from this function.
    """
    scores = {"BUY": 0.0, "SELL": 0.0, "WAIT": 0.0}
    for opinion in opinions.values():
        direction = opinion.direction.upper()
        if direction not in scores:
            continue
        confidence = min(max(float(opinion.confidence), 0.0), 1.0)
        scores[direction] += confidence
    best = max(scores, key=scores.get)
    ordered = sorted(scores.values(), reverse=True)
    margin = ordered[0] - ordered[1] if len(ordered) > 1 else ordered[0]
    decision = best if best != "WAIT" and margin >= 0.20 else "WAIT"
    return {"decision": decision, "scores": scores, "margin": margin, "execution": "DISABLED"}
