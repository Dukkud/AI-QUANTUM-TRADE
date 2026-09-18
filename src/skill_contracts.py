from dataclasses import dataclass
from typing import Mapping

ALLOWED_ACTIONS = frozenset({"READ", "ANALYZE", "PROPOSE", "VALIDATE"})
RISK_CLASSES = frozenset({"LOW", "MEDIUM", "HIGH"})

@dataclass(frozen=True)
class ContractViolation:
    field: str
    reason: str

def validate_skill_contract(manifest: Mapping[str, object]) -> tuple[ContractViolation, ...]:
    violations=[]
    required=("skill_id","version","purpose","allowed_agents","allowed_actions","risk_class","max_latency_ms","max_cost_units")
    for field in required:
        if field not in manifest or manifest[field] in (None, "", (), []):
            violations.append(ContractViolation(field,"required"))
    if manifest.get("risk_class") not in RISK_CLASSES:
        violations.append(ContractViolation("risk_class","invalid"))
    actions=manifest.get("allowed_actions", ())
    if isinstance(actions, (list, tuple, set, frozenset)):
        bad=set(actions)-ALLOWED_ACTIONS
        if bad: violations.append(ContractViolation("allowed_actions",f"unsupported:{sorted(bad)}"))
    else:
        violations.append(ContractViolation("allowed_actions","must_be_sequence"))
    if "EXECUTE" in actions if isinstance(actions,(list,tuple,set,frozenset)) else False:
        violations.append(ContractViolation("allowed_actions","EXECUTE_forbidden"))
    try:
        if int(manifest.get("max_latency_ms",0)) <= 0: violations.append(ContractViolation("max_latency_ms","must_be_positive"))
    except (TypeError,ValueError):
        violations.append(ContractViolation("max_latency_ms","invalid"))
    try:
        if float(manifest.get("max_cost_units",-1)) < 0: violations.append(ContractViolation("max_cost_units","must_be_nonnegative"))
    except (TypeError,ValueError):
        violations.append(ContractViolation("max_cost_units","invalid"))
    return tuple(violations)

def contract_is_valid(manifest: Mapping[str, object]) -> bool:
    return not validate_skill_contract(manifest)
