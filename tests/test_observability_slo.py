import pytest
from src.observability_slo import evaluate_slo

def test_slo_passes():
    assert evaluate_slo(.9995,.999,.995).status=='PASS'

def test_slo_review():
    assert evaluate_slo(.99,.999,.995).status=='REVIEW'

def test_invalid_slo_fails_closed():
    with pytest.raises(ValueError): evaluate_slo(1.01,.999,.995)
