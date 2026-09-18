from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class RecoveryDecision:
    status: str
    active_skill: str
    fallback_skill: str | None
    reason: str

def recover(skill_id: str, skill_failed: bool, fallback_skill: str | None = None) -> RecoveryDecision:
    if not skill_failed:
        return RecoveryDecision("ACTIVE", skill_id, fallback_skill, "HEALTHY")
    if fallback_skill:
        return RecoveryDecision("FALLBACK", skill_id, fallback_skill, "SKILL_DISABLED_NO_TRADING_STOP")
    return RecoveryDecision("DISABLED", skill_id, None, "SKILL_DISABLED_FAIL_CLOSED")
