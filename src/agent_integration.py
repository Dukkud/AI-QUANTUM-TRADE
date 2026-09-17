from dataclasses import dataclass
@dataclass(frozen=True)
class IntegrationResult:
    status:str
    reasons:tuple[str,...]
def validate_agent_skill_path(agent_id:str,skill_action:str,governor_status:str,execution_gate:str)->IntegrationResult:
    reasons=[]
    if governor_status!="ALLOW": reasons.append("governor_denied")
    if skill_action=="EXECUTE": reasons.append("skill_execution_forbidden")
    if execution_gate=="LIVE": reasons.append("integration_cannot_enable_live")
    return IntegrationResult("PASS" if not reasons else "FAIL",tuple(reasons))
