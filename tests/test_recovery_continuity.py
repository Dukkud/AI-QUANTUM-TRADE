import pytest
from src.recovery_continuity import evaluate_recovery

def test_recovery_pass():
    assert evaluate_recovery(backup_verified=True,ledger_restorable=True,replay_deterministic=True,rto_minutes=30,rpo_minutes=5).status=='PASS'

def test_recovery_review():
    r=evaluate_recovery(backup_verified=True,ledger_restorable=False,replay_deterministic=True,rto_minutes=30,rpo_minutes=5)
    assert r.status=='REVIEW' and 'LEDGER_RESTORE' in r.blockers

def test_invalid_target():
    with pytest.raises(ValueError): evaluate_recovery(backup_verified=True,ledger_restorable=True,replay_deterministic=True,rto_minutes=-1,rpo_minutes=5)
