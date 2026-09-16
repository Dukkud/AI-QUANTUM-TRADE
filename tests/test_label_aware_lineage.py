from datetime import datetime, timedelta, timezone

import pytest

from src.label_aware_lineage import LabeledPrediction, build_purged_split, overlaps, validate_lineage

BASE = datetime(2026, 1, 1, tzinfo=timezone.utc)


def lp(i, label_hours=2):
    start = BASE + timedelta(hours=i)
    end = start + timedelta(hours=label_hours)
    return LabeledPrediction(f"p-{i}", start.isoformat(), start.isoformat(), end.isoformat())


def test_prediction_ids_are_required_and_unique():
    with pytest.raises(ValueError, match="unique"):
        validate_lineage([lp(0), LabeledPrediction("p-0", lp(1).prediction_at_utc, lp(1).label_start_utc, lp(1).label_end_utc)])


def test_invalid_label_interval_fails_closed():
    p = lp(1)
    with pytest.raises(ValueError, match="precede"):
        validate_lineage([LabeledPrediction("bad", p.prediction_at_utc, (BASE - timedelta(hours=1)).isoformat(), p.label_end_utc)])


def test_overlap_is_interval_based():
    a = lp(0, 2)
    b = lp(1, 1)
    c = lp(3, 1)
    assert overlaps(a, b)
    assert not overlaps(a, c)


def test_label_aware_purge_removes_future_label_overlap():
    data = [lp(i, 2) for i in range(8)]
    # train p0-p1; validation p2-p3 labels end at hour 5.
    # p4-p5 are in the temporal embargo; p6 starts after the embargo but its
    # label interval overlaps validation only when the validation horizon is extended.
    split = build_purged_split(data, train_size=2, validation_size=2, oos_size=2, embargo=timedelta(hours=0))
    assert [x.prediction_id for x in split.train] == ["p-0", "p-1"]
    assert [x.prediction_id for x in split.validation] == ["p-2", "p-3"]
    assert [x.prediction_id for x in split.oos] == ["p-6", "p-7"]


def test_embargo_is_label_end_plus_gap():
    data = [lp(i, 2) for i in range(10)]
    split = build_purged_split(data, train_size=2, validation_size=2, oos_size=2, embargo=timedelta(hours=2))
    assert split.embargo
    assert split.oos[0].prediction_at_utc == (BASE + timedelta(hours=8)).isoformat()


def test_insufficient_leakage_safe_oos_fails_closed():
    with pytest.raises(ValueError, match="insufficient"):
        build_purged_split([lp(i, 5) for i in range(6)], train_size=2, validation_size=2, oos_size=2)
