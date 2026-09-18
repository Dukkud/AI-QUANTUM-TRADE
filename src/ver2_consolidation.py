"""VER2.0 consolidation readiness checks. Never authorizes live trading."""
from __future__ import annotations
from dataclasses import dataclass
from .agent_registry import validate_agent_registry
from .security_boundary import SecurityResult, validate_boundary

@dataclass(frozen=True)
class ConsolidationResult:
    status: str
    blockers: tuple[str, ...]

REQUIRED_CONTROL_LAYERS=("evidence","lineage","rolling_oos","calibration","risk","security","recovery","skills","qgraph","workgraph","workmachine")

def validate_consolidation(*, controls_present:set[str], live_trading:bool,
                           security_result:SecurityResult|None=None)->ConsolidationResult:
    blockers=list(validate_agent_registry())
    blockers.extend(f"MISSING_CONTROL_LAYER:{n}" for n in REQUIRED_CONTROL_LAYERS if n not in controls_present)
    if security_result is None:
        security_result=validate_boundary(live_trading=live_trading,paper_execution=True,adaptive_updates=False,api_key_in_env=True,secret_exposed=False)
    if security_result.status!="PASS": blockers.extend(f"SECURITY:{b}" for b in security_result.blockers)
    if live_trading: blockers.append("LIVE_TRADING_ENABLED")
    return ConsolidationResult("PASS" if not blockers else "BLOCKED",tuple(blockers))
