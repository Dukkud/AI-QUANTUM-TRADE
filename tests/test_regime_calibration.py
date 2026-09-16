import pytest

from src.regime_calibration import evaluate_regimes


def test_calibration_is_computed_per_regime():
    data = [("TREND", 0.8, True), ("TREND", 0.6, False)] * 20 + [("RANGE", 0.5, True)] * 10
    result = evaluate_regimes(data, min_samples=30)
    assert result["TREND"].samples == 40
    assert result["RANGE"].status == "INSUFFICIENT_EVIDENCE"
    assert result["TREND"].brier_score >= 0


def test_high_ece_triggers_review():
    data = [("TREND", 0.95, False)] * 30
    result = evaluate_regimes(data, min_samples=30, max_ece=0.10)
    assert result["TREND"].status == "CALIBRATION_REVIEW"
    assert result["TREND"].ece > 0.10


def test_invalid_observation_fails_closed():
    with pytest.raises(ValueError):
        evaluate_regimes([("TREND", 1.1, True)])


def test_empty_input_is_valid_but_has_no_regimes():
    assert evaluate_regimes([]) == {}
