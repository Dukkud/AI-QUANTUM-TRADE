import pytest
from src.skill_attribution import attribute_skill

def test_contribution_is_separated_from_agent_result():
    r=attribute_skill('web-research','Q6',1.0,1.2,0.20,0.15,30)
    assert r.samples==30
    assert r.contribution_r==pytest.approx(0.2)
    assert r.brier_delta==pytest.approx(0.05)

def test_zero_samples_fail_closed():
    with pytest.raises(ValueError): attribute_skill('x','Q1',0,1,0,0,0)
