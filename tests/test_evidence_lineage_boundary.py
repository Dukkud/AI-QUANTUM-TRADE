from src.evidence_lineage_boundary import LineageInputs,validate_lineage
def clean(): return LineageInputs("p1","e1",None,"s1","d1",True,True,True)
def test_clean(): assert validate_lineage(clean()).status=="PASS"
def test_identity_blocks():
    for f in ("prediction_id","evidence_id","source_id","dataset_id"):
        x=clean().__class__(**{**clean().__dict__,f:None})
        assert validate_lineage(x).status=="BLOCKED"
def test_integrity_blocks():
    for f in ("immutable_chain_valid","label_purge_valid"):
        x=clean().__class__(**{**clean().__dict__,f:False})
        assert validate_lineage(x).status=="BLOCKED"
def test_non_shadow_blocks():
    x=clean().__class__(**{**clean().__dict__,"shadow_only":False,"outcome_id":"o1"})
    assert validate_lineage(x).status=="BLOCKED"
