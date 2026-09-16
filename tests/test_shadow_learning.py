import pytest

from src.shadow_learning import LearningObservation, evaluate, learning_gate


def test_metrics_are_deterministic_and_per_agent():
    data = [
        LearningObservation("Q1", 0.9, True, 1.0),
        LearningObservation("Q1", 0.8, False, -1.0),
        LearningObservation("Q2", 0.6, True, 0.5),
    ]
    result = evaluate(data)
    assert result["Q1"].samples == 2
    assert result["Q1"].accuracy == 0.5
    assert result["Q1"].mean_realized_r == 0.0
    assert result["Q1"].win_rate == 0.5
    assert result["Q1"].max_drawdown_r == 1.0
    assert result["Q2"].brier_score == pytest.approx(0.16)


def test_invalid_confidence_is_rejected():
    with pytest.raises(ValueError):
        evaluate([LearningObservation("Q1", 1.1, True)])


def test_gate_requires_evidence_before_calibration_review():
    metrics = evaluate([LearningObservation("Q1", 0.99, False)] * 10)["Q1"]
    assert learning_gate(metrics, min_samples=30) == "INSUFFICIENT_EVIDENCE"


def test_gate_flags_poor_calibration_without_mutating_state():
    items = [LearningObservation("Q1", 0.99, False)] * 30
    metrics = evaluate(items)["Q1"]
    assert learning_gate(metrics, min_samples=30, max_brier=0.25) == "CALIBRATION_REVIEW"
