import pytest

from src.proposal_ledger import ProposalLedger


def test_ledger_chain_and_rollback():
    ledger = ProposalLedger()
    first = ledger.append("p1", {"Q1": 0.5, "Q2": 0.5}, "2026-01-01T00:00:00+00:00")
    second = ledger.append("p2", {"Q1": 0.6, "Q2": 0.4}, "2026-01-01T01:00:00+00:00")
    assert ledger.verify()
    assert second.parent_proposal_id == first.proposal_id
    assert ledger.rollback_target("p1") == first


def test_duplicate_id_and_missing_target_fail_closed():
    ledger = ProposalLedger()
    ledger.append("p1", {"Q1": 1.0}, "2026-01-01T00:00:00+00:00")
    with pytest.raises(ValueError, match="duplicate"):
        ledger.append("p1", {"Q1": 1.0}, "2026-01-01T01:00:00+00:00")
    with pytest.raises(KeyError):
        ledger.rollback_target("missing")


def test_tamper_is_detected():
    ledger = ProposalLedger()
    ledger.append("p1", {"Q1": 1.0}, "2026-01-01T00:00:00+00:00")
    ledger._records[0] = ledger._records[0].__class__("p1", None, {"Q1": 0.9}, ledger._records[0].created_at_utc, ledger._records[0].sha256)
    assert not ledger.verify()
