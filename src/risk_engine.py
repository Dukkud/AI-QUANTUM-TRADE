"""Fail-closed position sizing and live gate."""
from dataclasses import dataclass

@dataclass(frozen=True)
class RiskConfig:
    max_risk_pct: float = 0.50
    max_daily_loss_pct: float = 2.0
    max_open_risk_pct: float = 1.0

class RiskEngine:
    def __init__(self, cfg: RiskConfig = RiskConfig()): self.cfg = cfg
    def position_risk_pct(self, confidence: float, reduced: bool = False) -> float:
        base = self.cfg.max_risk_pct * max(0.0, min(1.0, confidence))
        return min(base * (0.5 if reduced else 1.0), self.cfg.max_risk_pct)
    def live_ready(self, gates: dict) -> bool:
        required = ('real_data_verified','data_quality_pass','reconciliation_pass','paper_execution_pass','risk_engine_pass','operator_enable','emergency_stop_clear')
        return all(bool(gates.get(k, False)) for k in required)
