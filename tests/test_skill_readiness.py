import pytest
from src.skill_readiness import CRITICAL, readiness

def test_all_critical_skill_gates_pass():
    r=readiness({name:True for name in CRITICAL})
    assert r.status=='PASS' and r.coverage==1.0 and r.blockers==()

def test_any_missing_critical_gate_blocks():
    gates={name:True for name in CRITICAL}; gates['sandbox']=False
    r=readiness(gates)
    assert r.status=='BLOCKED' and 'sandbox' in r.blockers

def test_invalid_coverage_is_rejected():
    with pytest.raises(ValueError): readiness({},1.1)
