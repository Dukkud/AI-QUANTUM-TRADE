import pytest
from src.forward_paper_gate import PaperStats, evaluate_forward_paper

def test_forward_paper_pass():
    assert evaluate_forward_paper(PaperStats(100, 2.0, 3.0, .995)).status == 'PASS'

def test_forward_paper_blocks_bad_settlement():
    r=evaluate_forward_paper(PaperStats(100,2,3,.90))
    assert r.status=='REVIEW' and 'SETTLEMENT_COMPLETENESS' in r.blockers

def test_invalid_values_fail_closed():
    with pytest.raises(ValueError): evaluate_forward_paper(PaperStats(100,float('nan'),1,.99))
