import pytest

from src.statistical_evidence import bootstrap_mean_interval, evaluate, wilson_interval


def test_wilson_interval_bounds_and_point_coverage():
    ci = wilson_interval(15, 20)
    assert 0.0 <= ci.lower < 0.75 < ci.upper <= 1.0


def test_wilson_rejects_invalid_inputs():
    with pytest.raises(ValueError):
        wilson_interval(21, 20)


def test_bootstrap_is_deterministic():
    values = [1.0, 0.5, -0.5, 1.5] * 10
    a = bootstrap_mean_interval(values, iterations=500, seed=7)
    b = bootstrap_mean_interval(values, iterations=500, seed=7)
    assert a == b
    assert a.lower <= 0.625 <= a.upper


def test_evidence_gate_blocks_small_sample():
    result = evaluate([True] * 10, [1.0] * 10, min_samples=30)
    assert result.status == "INSUFFICIENT_EVIDENCE"
    assert result.samples == 10
    assert result.mean_r_ci is None


def test_evidence_gate_ready_with_sufficient_sample():
    correct = [True, False] * 20
    realized = [1.0, -0.5] * 20
    result = evaluate(correct, realized, min_samples=30)
    assert result.status == "EVIDENCE_READY"
    assert result.samples == 40
    assert result.mean_r_ci is not None


def test_realized_length_mismatch_fails_closed():
    with pytest.raises(ValueError, match="length"):
        evaluate([True] * 30, [1.0] * 29)
