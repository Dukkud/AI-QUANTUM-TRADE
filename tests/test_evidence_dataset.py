from datetime import datetime, timedelta, timezone

import pytest

from src.evidence_dataset import build_leakage_safe_windows, build_manifest, fingerprint, reject_duplicate_observations
from src.rolling_oos import OOSObservation

BASE = datetime(2026, 1, 1, tzinfo=timezone.utc)


def obs(i):
    return OOSObservation((BASE + timedelta(hours=i)).isoformat(), "XAUUSD", "1H", "TREND", "Q1", 0.8, i % 2 == 0, 1.0)


def test_manifest_is_deterministic_and_fingerprint_changes_on_content_change():
    data = [obs(i) for i in range(5)]
    a = build_manifest(data, "dataset-v1")
    b = build_manifest(list(reversed(data)), "dataset-v1")
    assert a.sha256 == b.sha256
    assert a.observation_count == 5
    changed = list(data)
    changed[0] = OOSObservation(changed[0].timestamp_utc, "XAUUSD", "1H", "TREND", "Q1", 0.7, True, 1.0)
    assert fingerprint(changed) != a.sha256


def test_duplicate_observations_fail_closed():
    with pytest.raises(ValueError, match="duplicate"):
        reject_duplicate_observations([obs(1), obs(1)])


def test_embargo_separates_validation_and_oos():
    data = [obs(i) for i in range(12)]
    windows = build_leakage_safe_windows(data, train_size=4, validation_size=3, embargo=timedelta(hours=2), oos_size=2)
    assert windows
    w = windows[0]
    assert (datetime.fromisoformat(w.oos[0].timestamp_utc) - datetime.fromisoformat(w.validation[-1].timestamp_utc)) >= timedelta(hours=2)
    # With hourly observations, validation ends at hour 6 and the first
    # post-validation observation is hour 7; only hour 7 lies strictly inside
    # the two-hour embargo [7, 8).
    assert len(w.embargo) == 1


def test_negative_embargo_rejected():
    with pytest.raises(ValueError):
        build_leakage_safe_windows([obs(i) for i in range(10)], train_size=3, validation_size=2, embargo=timedelta(hours=-1), oos_size=2)
