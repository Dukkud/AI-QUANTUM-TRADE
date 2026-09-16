from src.gold_triangulation import GoldTriangulationEngine, GoldTriangulationError, observations_from_rows


def sample_rows():
    return [
        {"timestamp": "2026-09-16T10:00:00+00:00", "timeframe": "1H", "xauusd": 100.0, "paxg": 100.1, "xaut": 99.9},
        {"timestamp": "2026-09-16T11:00:00+00:00", "timeframe": "1H", "xauusd": 101.0, "paxg": 101.1, "xaut": 100.9},
        {"timestamp": "2026-09-16T12:00:00+00:00", "timeframe": "1H", "xauusd": 100.5, "paxg": 100.6, "xaut": 100.4},
        {"timestamp": "2026-09-16T13:00:00+00:00", "timeframe": "1H", "xauusd": 102.0, "paxg": 102.1, "xaut": 101.9},
    ]


def test_triangulation_is_descriptive_and_cannot_change_weights():
    obs = observations_from_rows(sample_rows())
    result = GoldTriangulationEngine().analyze(obs)
    assert result["research_only"] is True
    assert result["live_execution"] is False
    assert result["decision"] == "EVIDENCE_ONLY"
    assert result["weight_update"] is False
    assert set(result["correlation"]) == {"PAXG_XAUUSD", "XAUT_XAUUSD", "PAXG_XAUT"}


def test_cross_asset_relationships_are_numeric():
    result = GoldTriangulationEngine().analyze(observations_from_rows(sample_rows()))
    assert result["observations"] == 4
    assert result["correlation"]["PAXG_XAUUSD"] is not None
    assert result["basis"]["PAXG_XAUUSD_last"] > 0
    assert len(result["lead_lag"]["PAXG_XAUUSD"]) == 7


def test_duplicate_timestamp_fails_closed():
    rows = sample_rows(); rows[-1]["timestamp"] = rows[-2]["timestamp"]
    try:
        GoldTriangulationEngine().analyze(observations_from_rows(rows))
    except GoldTriangulationError:
        return
    raise AssertionError("duplicate timestamps must fail closed")


def test_non_positive_prices_fail_closed():
    rows = sample_rows(); rows[2]["paxg"] = 0
    try:
        GoldTriangulationEngine().analyze(observations_from_rows(rows))
    except GoldTriangulationError:
        return
    raise AssertionError("non-positive prices must fail closed")
