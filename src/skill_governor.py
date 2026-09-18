from __future__ import annotations
from dataclasses import dataclass
from src.skill_registry import SkillRegistry

@dataclass(frozen=True)
class SkillRequest:
    skill_id: str
    agent_id: str
    action: str
    asset: str
    timeframe: str
    regime: str

@dataclass(frozen=True)
class GovernorDecision:
    status: str
    reason: str

class SkillGovernor:
    """Fail-closed dispatcher. Skills cannot authorize themselves or execute trades."""
    def __init__(self, registry: SkillRegistry) -> None:
        self.registry = registry

    def authorize(self, request: SkillRequest) -> GovernorDecision:
        try:
            allowed = self.registry.authorize(request.skill_id, request.agent_id, request.action)
        except KeyError:
            return GovernorDecision("BLOCKED", "UNKNOWN_SKILL")
        if request.action == "EXECUTE":
            return GovernorDecision("BLOCKED", "SKILL_EXECUTION_FORBIDDEN")
        if not allowed:
            return GovernorDecision("BLOCKED", "POLICY_DENIED")
        return GovernorDecision("ALLOW", "AUTHORIZED")
