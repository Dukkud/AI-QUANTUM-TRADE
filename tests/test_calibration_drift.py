import pytest

from src.calibration_drift import DriftSnapshot, DriftThresholds, compare


def snap(**kwargs):
    base = dict(agent="Q7", samples=100, accuracy=0.60, brier_score=0.20,
                mean_realized_r=0.40, mean_confidence=0.60)
    base.update(kwargs)
    return DriftSnapshot(**base)


def test_stable_snapshot_is_deterministic():
    result = compare(snap(), snap())
    assert result.status == "STABLE"
    assert result.reasons == ()
    assert result.accuracy_delta == 0.0
    assert result.brier_delta == 0.0


def test_insufficient_evidence_blocks_drift_conclusion():
    result = compare(snap(samples=29), snap(samples=100, accuracy=0.10))
    assert result.status == "INSUFFICIENT_EVIDENCE"
    assert result.reasons == ("minimum sample threshold not met",)


def test_material_drift_is_flagged_without_mutation():
    baseline = snap()
    current = snap(accuracy=0.40, brier_score=0.28, mean_realized_r=-0.30,
                    mean_confidence=0.78)
    result = compare(baseline, current)
    assert result.status == "DRIFT_REVIEW"
    assert result.reasons == ("accuracy_drop", "brier_increase", "realized_r_drop", "confidence_shift")
    assert baseline.accuracy == 0.60
    assert current.accuracy == 0.40


def test_threshold_boundary_is_not_flagged():
    result = compare(snap(), snap(accuracy=0.50, brier_score=0.25,
                                  mean_realized_r=-0.10, mean_confidence=0.70))
    assert result.status == "STABLE"


def test_agent_mismatch_is_rejected():
    with pytest.raises(ValueError):
        compare(snap(agent="Q1"), snap(agent="Q2"))


def test_invalid_metric_is_rejected():
    with pytest.raises(ValueError):
        compare(snap(), snap(brier_score=-0.1))


def test_custom_thresholds_are_explicit():
    result = compare(snap(), snap(accuracy=0.55),
                     DriftThresholds(max_accuracy_drop=0.04))
    assert result.status == "DRIFT_REVIEW"
    assert result.reasons == ("accuracy_drop",)
