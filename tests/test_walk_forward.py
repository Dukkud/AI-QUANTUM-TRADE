import pytest

from src.walk_forward import WindowScore, evaluate_stability


def test_stable_windows():
    report = evaluate_stability([
        WindowScore(40, 0.60, 0.30, 1.0),
        WindowScore(40, 0.62, 0.20, 1.5),
        WindowScore(40, 0.58, 0.25, 1.2),
    ])
    assert report.status == "STABLE"
    assert report.windows == 3


def test_small_window_blocks_stability():
    report = evaluate_stability([WindowScore(29, 0.9, 1.0, 0.0)])
    assert report.status == "INSUFFICIENT_EVIDENCE"


def test_accuracy_dispersion_triggers_review():
    report = evaluate_stability([
        WindowScore(40, 0.95, 0.5, 1.0),
        WindowScore(40, 0.55, 0.1, 1.0),
    ], max_accuracy_std=0.10)
    assert report.status == "STABILITY_REVIEW"
    assert "dispersion" in report.reason


def test_drawdown_triggers_review():
    report = evaluate_stability([WindowScore(40, 0.60, 0.1, 6.0)])
    assert report.status == "STABILITY_REVIEW"
    assert "drawdown" in report.reason


def test_invalid_score_fails_closed():
    with pytest.raises(ValueError):
        evaluate_stability([WindowScore(40, 1.1, 0.1, 1.0)])
