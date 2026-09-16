import pytest

from src.adaptive_shadow import propose_weights

AGENTS = {f"Q{i}": 0.125 for i in range(1, 9)}
SCORES = {f"Q{i}": 0.5 + i / 100 for i in range(1, 9)}


def test_hold_when_evidence_gate_not_ready():
    result = propose_weights(AGENTS, SCORES, evidence_ready=False, stability_status="STABLE")
    assert result.status == "HOLD"
    assert result.proposed_weights == result.base_weights


def test_hold_when_stability_review():
    result = propose_weights(AGENTS, SCORES, evidence_ready=True, stability_status="STABILITY_REVIEW")
    assert result.status == "HOLD"


def test_proposal_is_bounded_and_unit_sum():
    result = propose_weights(AGENTS, SCORES, evidence_ready=True, stability_status="STABLE", max_weight=0.20)
    assert result.status == "PROPOSED"
    assert abs(sum(result.proposed_weights.values()) - 1.0) < 1e-9
    assert all(0.02 <= v <= 0.20 for v in result.proposed_weights.values())


def test_input_weights_are_not_mutated():
    before = dict(AGENTS)
    propose_weights(AGENTS, SCORES, evidence_ready=True, stability_status="STABLE")
    assert AGENTS == before


def test_agent_set_mismatch_fails_closed():
    with pytest.raises(ValueError, match="match agents"):
        propose_weights(AGENTS, {"Q1": 1.0}, evidence_ready=True, stability_status="STABLE")


def test_infeasible_bounds_rejected():
    with pytest.raises(ValueError, match="unit-sum"):
        propose_weights(AGENTS, SCORES, evidence_ready=True, stability_status="STABLE", min_weight=0.2, max_weight=0.21)
