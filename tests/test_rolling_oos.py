from datetime import datetime, timedelta, timezone

from src.rolling_oos import OOSObservation, build_rolling_windows, metrics, segment


BASE = datetime(2026, 1, 1, tzinfo=timezone.utc)


def obs(i: int, asset: str = "XAUUSD", regime: str = "TREND") -> OOSObservation:
    return OOSObservation(
        timestamp_utc=(BASE + timedelta(hours=i)).isoformat(),
        asset=asset,
        timeframe="1H",
        regime=regime,
        agent="Q1",
        confidence=0.8 if i % 2 == 0 else 0.3,
        correct=i % 2 == 0,
        realized_r=1.0 if i % 3 else -0.5,
    )


def test_rolling_windows_are_chronological_and_nonempty():
    windows = build_rolling_windows([obs(i) for i in range(100)], train_size=50, validation_size=20, oos_size=20, step=10)
    assert len(windows) == 2
    assert len(windows[0].train) == 50
    assert len(windows[0].validation) == 20
    assert len(windows[0].oos) == 20
    assert windows[0].train[-1].timestamp_utc < windows[0].validation[0].timestamp_utc < windows[0].oos[0].timestamp_utc
    assert windows[1].train[0].timestamp_utc > windows[0].train[0].timestamp_utc


def test_insufficient_history_produces_no_window():
    assert build_rolling_windows([obs(i) for i in range(89)], train_size=50, validation_size=20, oos_size=20, step=10) == []


def test_segment_filters_exact_dimensions():
    data = [obs(0), obs(1, asset="BTCUSDT"), obs(2, regime="RANGE")]
    result = segment(data, asset="XAUUSD", timeframe="1H", regime="TREND", agent="Q1")
    assert len(result) == 1
    assert result[0].asset == "XAUUSD"


def test_metrics_are_deterministic_and_do_not_mutate():
    data = [obs(i) for i in range(4)]
    before = tuple(data)
    result = metrics(data)
    assert result.samples == 4
    assert result.accuracy == 0.5
    assert result.brier_score == 0.25
    assert result.mean_realized_r == 0.625
    assert result.max_drawdown_r == 0.5
    assert tuple(data) == before


def test_invalid_timestamp_and_confidence_fail_closed():
    bad_time = OOSObservation("2026-01-01T00:00:00", "XAUUSD", "1H", "TREND", "Q1", 0.5, True)
    try:
        metrics([bad_time])
        assert False, "expected ValueError"
    except ValueError:
        pass
    bad_conf = OOSObservation("2026-01-01T00:00:00+00:00", "XAUUSD", "1H", "TREND", "Q1", 1.1, True)
    try:
        metrics([bad_conf])
        assert False, "expected ValueError"
    except ValueError:
        pass
