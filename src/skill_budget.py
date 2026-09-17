from __future__ import annotations
from dataclasses import dataclass
from src.skill_registry import SkillManifest

@dataclass(frozen=True)
class BudgetDecision:
    status: str
    reason: str

def check_budget(manifest: SkillManifest, latency_ms: int, cost_units: float) -> BudgetDecision:
    if latency_ms < 0 or cost_units < 0:
        return BudgetDecision("BLOCKED", "INVALID_MEASUREMENT")
    if latency_ms > manifest.max_latency_ms:
        return BudgetDecision("BLOCKED", "LATENCY_BUDGET")
    if cost_units > manifest.max_cost_units:
        return BudgetDecision("BLOCKED", "COST_BUDGET")
    return BudgetDecision("PASS", "WITHIN_BUDGET")
