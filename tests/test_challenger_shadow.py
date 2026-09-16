import math
import pytest

from src.challenger_shadow import compare_locked_oos


def test_locked_paired_comparison():
    result = compare_locked_oos(dataset_id="oos-v1", dataset_sha256="abc123", baseline_r=[0.0, 1.0] * 20, challenger_r=[0.5, 1.0] * 20, baseline_correct=[False, True] * 20, challenger_correct=[True, True] * 20)
    assert result.status == "OBSERVE"
    assert result.samples == 40
    assert result.delta_mean_r == 0.25
    assert result.challenger_accuracy == 1.0


def test_small_sample_is_not_promoted():
    result = compare_locked_oos(dataset_id="oos-v1", dataset_sha256="abc", baseline_r=[1.0] * 10, challenger_r=[2.0] * 10, baseline_correct=[True] * 10, challenger_correct=[True] * 10)
    assert result.status == "INSUFFICIENT_EVIDENCE"


def test_mismatched_pairs_fail_closed():
    with pytest.raises(ValueError, match="equal"):
        compare_locked_oos(dataset_id="oos", dataset_sha256="abc", baseline_r=[1.0] * 30, challenger_r=[1.0] * 29, baseline_correct=[True] * 30, challenger_correct=[True] * 30)


def test_missing_identity_fails_closed():
    with pytest.raises(ValueError, match="identity"):
        compare_locked_oos(dataset_id="", dataset_sha256="abc", baseline_r=[1.0] * 30, challenger_r=[1.0] * 30, baseline_correct=[True] * 30, challenger_correct=[True] * 30)
