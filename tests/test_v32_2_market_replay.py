from src.market_replay import MarketBar, dataset_fingerprint, replay, validate_dataset


def bars():
    return [
        MarketBar(0, "XAUUSD", "1M", 2500, 2502, 2499, 2501, 10, 2500.9, 2501.1),
        MarketBar(60000, "XAUUSD", "1M", 2501, 2504, 2500, 2503, 11, 2502.9, 2503.1),
        MarketBar(120000, "XAUUSD", "1M", 2503, 2505, 2502, 2504, 12, 2503.9, 2504.1),
    ]


def test_valid_dataset_and_native_quotes():
    result = validate_dataset(bars())
    assert result["valid"] is True
    assert result["bars"] == 3
    assert result["native_quotes"] is True
    assert result["gaps"] == []


def test_invalid_dataset_fails_closed_without_repair():
    bad = list(bars())
    bad[1] = MarketBar(60000, "XAUUSD", "1M", 2501, 2490, 2500, 2503)
    result = validate_dataset(bad)
    assert result["valid"] is False
    assert any("invalid OHLC" in error for error in result["errors"])


def test_duplicate_and_non_monotonic_timestamps_are_rejected():
    bad = list(bars())
    bad[2] = MarketBar(60000, "XAUUSD", "1M", 2503, 2505, 2502, 2504)
    result = validate_dataset(bad)
    assert result["valid"] is False
    assert any("duplicate timestamp" in error for error in result["errors"])
    assert any("strictly increasing" in error for error in result["errors"])


def test_gaps_are_reported_not_silently_filled():
    bad = list(bars())
    bad[2] = MarketBar(180000, "XAUUSD", "1M", 2503, 2505, 2502, 2504)
    result = validate_dataset(bad)
    assert result["valid"] is True
    assert len(result["gaps"]) == 1
    assert result["gaps"][0]["delta_ms"] == 120000


def test_fingerprint_and_replay_are_deterministic_and_research_only():
    first = replay(bars())
    second = replay(bars())
    assert first == second
    assert len(first[0]["dataset_fingerprint"]) == 64
    assert first[0]["previous_close"] is None
    assert first[1]["previous_close"] == 2501
    assert all(event["research_only"] is True for event in first)
    assert all(event["live_execution"] is False for event in first)
    assert dataset_fingerprint(bars()) == first[0]["dataset_fingerprint"]
