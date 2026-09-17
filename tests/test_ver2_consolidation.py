from src.agent_registry import required_agent_ids, validate_agent_registry
from src.q9_self_learning import evaluate_q9
from src.ver2_consolidation import REQUIRED_CONTROL_LAYERS, validate_consolidation


def test_q1_to_q9_registry():
    assert required_agent_ids() == tuple(f"Q{i}" for i in range(1, 10))
    assert validate_agent_registry() == ()


def test_q9_fail_closed():
    assert evaluate_q9(
        evidence_ok=True, oos_ok=True, calibration_ok=True,
        production_mutation_requested=True, live_trading_requested=False
    ).status == "BLOCKED"


def test_ver2_consolidation_passes_without_live_execution():
    result = validate_consolidation(
        controls_present=set(REQUIRED_CONTROL_LAYERS),
        live_trading=False,
    )
    assert result.status == "PASS"


def test_ver2_consolidation_blocks_missing_control():
    result = validate_consolidation(
        controls_present=set(REQUIRED_CONTROL_LAYERS) - {"evidence"},
        live_trading=False,
    )
    assert result.status == "BLOCKED"
