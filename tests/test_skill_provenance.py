from src.skill_provenance import SkillInvocation, canonical_hash, invocation_hash

def test_canonical_hash_is_stable_and_order_independent():
    assert canonical_hash({'b':2,'a':1}) == canonical_hash({'a':1,'b':2})

def test_invocation_hash_is_deterministic_and_changes_on_evidence_change():
    base = SkillInvocation('web-research','1','Q6','p1','XAUUSD','1H','TREND',canonical_hash({'x':1}),('src1',),('READ',),canonical_hash({'y':2}),.7,20,1,'2026-01-01T00:00:00Z','ALLOW')
    changed = SkillInvocation(**{**base.__dict__, 'source_ids': ('src2',)})
    assert invocation_hash(base) == invocation_hash(base)
    assert invocation_hash(base) != invocation_hash(changed)
