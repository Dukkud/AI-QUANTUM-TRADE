import pytest
from src.locked_oos_challenger import ChallengerMetrics, compare_locked_oos


def m(model, r, acc=.6, brier=.2, n=100):
    return ChallengerMetrics(model, n, r, acc, brier)


def test_challenger_passes_locked_oos():
    result = compare_locked_oos(m('base', .10), m('challenger', .15))
    assert result.status == 'PASS'
    assert result.delta_mean_r == pytest.approx(.05)


def test_brier_worsening_requires_review():
    result = compare_locked_oos(m('base', .10, brier=.20), m('challenger', .11, brier=.21))
    assert result.status == 'REVIEW'


def test_insufficient_or_mismatched_samples_fail_closed():
    with pytest.raises(ValueError):
        compare_locked_oos(m('base', .1, n=99), m('challenger', .2, n=99))
    with pytest.raises(ValueError):
        compare_locked_oos(m('same', .1), m('same', .2))


def test_nonfinite_metrics_fail_closed():
    with pytest.raises(ValueError):
        compare_locked_oos(m('base', float('nan')), m('challenger', .2))
