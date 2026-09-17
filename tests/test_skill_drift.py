import pytest
from src.skill_drift import detect_drift

def test_drift_and_stability_threshold():
    assert detect_drift(.10,.17,.05).status=='DRIFT'
    assert detect_drift(.10,.15,.05).status=='STABLE'

def test_invalid_inputs_fail_closed():
    with pytest.raises(ValueError): detect_drift(float('nan'),.1)
    with pytest.raises(ValueError): detect_drift(.1,.1,-.01)
