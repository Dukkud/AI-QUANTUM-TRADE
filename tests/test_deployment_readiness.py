from src.deployment_readiness import ReadinessInputs, evaluate_readiness

def test_ready_requires_every_gate():
    x = ReadinessInputs(True, True, True, True, True, True)
    assert evaluate_readiness(x).status == 'READY_FOR_PAPER_PROMOTION'

def test_missing_gate_is_blocked():
    x = ReadinessInputs(True, True, False, True, True, True)
    r = evaluate_readiness(x)
    assert r.status == 'BLOCKED' and 'RECONCILIATION' in r.blockers

def test_live_flag_can_never_pass():
    x = ReadinessInputs(True, True, True, True, True, True, True)
    assert evaluate_readiness(x).status == 'BLOCKED'
