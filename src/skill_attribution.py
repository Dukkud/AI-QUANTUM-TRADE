from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Attribution:
    skill_id: str
    agent_id: str
    samples: int
    contribution_r: float
    brier_delta: float

def attribute_skill(skill_id: str, agent_id: str, baseline_r: float, skill_r: float, baseline_brier: float, skill_brier: float, samples: int) -> Attribution:
    if samples < 1:
        raise ValueError("samples must be positive")
    return Attribution(skill_id, agent_id, samples, skill_r - baseline_r, baseline_brier - skill_brier)
