from src.q9_self_learning import evaluate_q9
from src.evidence_lineage_boundary import LineageInputs,validate_lineage
def test_invalid_lineage_blocks_q9():
    l=LineageInputs("p1","e1",None,"s1","d1",False,True,True)
    assert validate_lineage(l).status=="BLOCKED"
    assert evaluate_q9(evidence_ok=False,oos_ok=True,calibration_ok=True,production_mutation_requested=False,live_trading_requested=False).status=="BLOCKED"
def test_valid_lineage_stays_shadow():
    l=LineageInputs("p1","e1",None,"s1","d1",True,True,True)
    assert validate_lineage(l).status=="PASS"
    assert evaluate_q9(evidence_ok=True,oos_ok=True,calibration_ok=True,production_mutation_requested=False,live_trading_requested=False).status=="SHADOW_LEARNING"
