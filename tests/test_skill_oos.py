import pytest
from src.skill_oos import evaluate_skill_oos

def test_insufficient_evidence_is_not_pass():
    assert evaluate_skill_oos([0.2,-0.1],0.1,min_samples=3).status=="INSUFFICIENT_EVIDENCE"

def test_positive_shadow_oos_passes_and_bad_brier_fails():
    assert evaluate_skill_oos([0.2,0.1,-0.05],0.10,min_samples=3).status=="PASS_SHADOW"
    assert evaluate_skill_oos([0.2,0.1,-0.05],0.30,min_samples=3).status=="FAIL_SHADOW"

def test_non_finite_data_is_rejected():
    with pytest.raises(ValueError): evaluate_skill_oos([0.1,float('inf')],0.1,min_samples=2)
