import pytest

from src.multiple_testing import alpha_spending, holm_bonferroni


def test_linear_alpha_spending_is_monotonic():
    assert alpha_spending(1, 4).alpha_spent == pytest.approx(0.0125)
    assert alpha_spending(4, 4).alpha_spent == pytest.approx(0.05)


def test_holm_controls_multiple_comparisons():
    decisions = holm_bonferroni([0.01, 0.02, 0.20])
    assert decisions == [True, False, False]


def test_invalid_inputs_fail_closed():
    with pytest.raises(ValueError):
        alpha_spending(5, 4)
    with pytest.raises(ValueError):
        holm_bonferroni([0.01, 1.1])
