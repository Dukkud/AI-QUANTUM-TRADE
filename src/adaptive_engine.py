"""Adaptive agent reputation; safety gates are immutable here."""
from dataclasses import dataclass

@dataclass
class AgentScore:
    calibration: float = 0.5
    ev: float = 0.0
    robustness: float = 0.5
    regime_score: float = 0.5
    independence: float = 0.5
    drawdown_penalty: float = 0.0
    active: bool = True
    def score(self) -> float:
        return max(0.0, self.calibration + self.ev + self.robustness + self.regime_score + self.independence - self.drawdown_penalty)

class AdaptiveEngine:
    def __init__(self, agents=None): self.agents = agents or {f'Q{i}': AgentScore() for i in range(1,9)}
    def weights(self):
        live = {k:v for k,v in self.agents.items() if v.active}
        total = sum(v.score() for v in live.values()) or 1.0
        return {k: v.score()/total for k,v in live.items()}
    def quarantine(self, agent: str):
        if agent in self.agents: self.agents[agent].active = False
