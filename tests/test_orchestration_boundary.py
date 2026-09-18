from src.orchestration_boundary import OrchestrationInputs,validate_orchestration
def clean(): return OrchestrationInputs(True,True,True,True,True,False)
def test_clean(): assert validate_orchestration(clean()).status=="PASS"
def test_each_gate_blocks():
    for f in ("evidence_ok","oos_ok","calibration_ok","risk_ok","security_ok"):
        x=clean().__class__(**{**clean().__dict__,f:False})
        assert validate_orchestration(x).status=="BLOCKED"
def test_live_blocks():
    x=clean().__class__(**{**clean().__dict__,"live_trading":True})
    assert validate_orchestration(x).status=="BLOCKED"
