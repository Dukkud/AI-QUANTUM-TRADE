from src.agent_registry import required_agent_ids,validate_agent_registry
from src.q9_self_learning import evaluate_q9
from src.security_boundary import validate_boundary
from src.ver2_consolidation import REQUIRED_CONTROL_LAYERS,validate_consolidation
def sec(**kw): return validate_boundary(live_trading=False,paper_execution=True,adaptive_updates=False,api_key_in_env=True,secret_exposed=False,**kw)
def test_q1_q9(): assert required_agent_ids()==tuple(f"Q{i}" for i in range(1,10)) and validate_agent_registry()==()
def test_q9_fail_closed(): assert evaluate_q9(evidence_ok=True,oos_ok=True,calibration_ok=True,production_mutation_requested=True,live_trading_requested=False).status=="BLOCKED"
def test_consolidation_pass(): assert validate_consolidation(controls_present=set(REQUIRED_CONTROL_LAYERS),live_trading=False,security_result=sec()).status=="PASS"
def test_security_failure_blocks(): assert validate_consolidation(controls_present=set(REQUIRED_CONTROL_LAYERS),live_trading=False,security_result=sec(live_trading=True)).status=="BLOCKED"
def test_missing_control_blocks(): assert validate_consolidation(controls_present=set(REQUIRED_CONTROL_LAYERS)-{"evidence"},live_trading=False,security_result=sec()).status=="BLOCKED"
