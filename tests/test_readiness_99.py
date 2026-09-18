from src.readiness_99 import evaluate_99

def test_99_requires_critical_gates():
    gates={k:True for k in ('data','lineage','oos','risk','paper','security','recovery','observability','provenance','stats')}
    r=evaluate_99(gates)
    assert r.score==100 and r.status=='READY_99_RESEARCH_PAPER'

def test_missing_critical_gate_blocks_even_if_score_high():
    gates={k:True for k in ('data','lineage','oos','risk','paper','security','recovery','observability','provenance','stats')}
    gates['risk']=False
    assert evaluate_99(gates).status=='BLOCKED'

def test_noncritical_single_gap_below_threshold():
    gates={k:True for k in ('data','lineage','oos','risk','paper','security','recovery','observability','provenance','stats')}
    gates['observability']=False
    assert evaluate_99(gates).score==90
