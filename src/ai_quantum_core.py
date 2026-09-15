"""AI-QUANTUM v30 deterministic decision core."""
from dataclasses import dataclass
from typing import Literal

Decision = Literal["APPROVE", "APPROVE_REDUCED_SIZE", "WAIT", "NO_TRADE", "EMERGENCY_EXIT"]

@dataclass(frozen=True)
class TradeCandidate:
    asset: str
    timeframe: str
    direction: str
    entry: float
    stop: float
    target: float
    probability: float
    avg_win_r: float
    avg_loss_r: float
    data_quality: float
    news_risk: float = 0.0
    agent_agreement: float = 0.0

    @property
    def rr(self) -> float:
        risk = abs(self.entry - self.stop)
        return abs(self.target - self.entry) / risk if risk else 0.0

    @property
    def ev_r(self) -> float:
        p = max(0.0, min(1.0, self.probability))
        return p * self.avg_win_r - (1.0 - p) * self.avg_loss_r

class QuantumCore:
    """Combines evidence without majority-vote logic and fails closed."""
    def decide(self, c: TradeCandidate) -> Decision:
        if c.data_quality < 0.95:
            return "NO_TRADE"
        if c.news_risk >= 0.85:
            return "WAIT"
        if c.rr < 1.2 or c.ev_r <= 0:
            return "NO_TRADE"
        if c.agent_agreement < 0.45:
            return "WAIT"
        if c.probability < 0.55:
            return "NO_TRADE"
        return "APPROVE" if c.agent_agreement >= 0.70 else "APPROVE_REDUCED_SIZE"
