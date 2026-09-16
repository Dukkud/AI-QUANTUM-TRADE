from src.evidence_events import OutcomeEvent, PredictionEvent, agent_realized_contribution, validate_link


def prediction(pid="p1"):
    return PredictionEvent("p1" if pid == "p1" else pid, "2026-09-16T10:00:00Z", "XAUUSD", "1H", "APPROVE", "LONG", 2500, 2490, 2520, .7, {"Q7": {"confidence": .8}})


def test_prediction_outcome_join_key():
    p = prediction()
    assert validate_link(p, OutcomeEvent("p1", "2026-09-16T11:00:00Z", "CLOSED", realized_r=1.5))
    assert not validate_link(p, OutcomeEvent("other", "2026-09-16T11:00:00Z", "CLOSED", realized_r=1.5))


def test_attribution_is_descriptive_and_deterministic():
    assert agent_realized_contribution({"confidence": .8}, 2.0) == 1.6
    assert agent_realized_contribution({"confidence": 2.0}, -1.0) == -1.0
    assert agent_realized_contribution({}, 1.0) is None
    assert agent_realized_contribution({"confidence": .8}, None) is None
