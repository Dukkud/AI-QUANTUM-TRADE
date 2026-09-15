from src.github_integrations.midas_adapter import CouncilOpinion, aggregate, council_contract
from src.github_integrations.pine_reference import route_topics, validate_script
from src.github_integrations.registry import integration_registry
from src.github_integrations.xau_research import atr, ema, features, regime, rsi, structure


def _bars(n=60):
    bars = []
    for i in range(n):
        base = 2000.0 + i * 1.5
        bars.append({"open": base - 0.5, "high": base + 2.0, "low": base - 1.0, "close": base})
    return bars


def test_registry_is_research_only():
    registry = integration_registry()
    assert registry["pine_v6"]["execution"] is False
    assert registry["midas"]["execution"] is False
    assert registry["xau_research"]["execution"] is False
    assert registry["policy"]["live_orders"] is False
    assert registry["policy"]["paper_only"] is True


def test_pine_validator_is_conservative():
    result = validate_script("//@version=6\nstrategy('x')\nrequest.security(syminfo.tickerid, '60', close, lookahead=barmerge.lookahead_on)")
    assert result.ok is True
    assert "review_mtf_lookahead_interaction" in result.warnings
    assert "request.security" in result.matched_review_terms
    assert "execution_model.md" in route_topics(["execution_model"])


def test_pine_validator_rejects_empty_script():
    result = validate_script("")
    assert result.ok is False
    assert "empty_script" in result.errors


def test_midas_contract_has_specialists_and_disabled_execution():
    contract = council_contract()
    assert set(contract["specialists"]) == {"fundamentals", "sentiment", "news", "technical"}
    assert contract["execution"] == "DISABLED"
    opinions = {
        "a": CouncilOpinion("technical", "BUY", 0.8, "trend"),
        "b": CouncilOpinion("news", "BUY", 0.7, "macro"),
        "c": CouncilOpinion("risk", "SELL", 0.1, "risk"),
    }
    result = aggregate(opinions)
    assert result["decision"] == "BUY"
    assert result["execution"] == "DISABLED"


def test_midas_tie_becomes_wait():
    opinions = {
        "a": CouncilOpinion("technical", "BUY", 0.8, "x"),
        "b": CouncilOpinion("news", "SELL", 0.8, "y"),
    }
    assert aggregate(opinions)["decision"] == "WAIT"


def test_xau_indicators_are_deterministic():
    bars = _bars()
    closes = [b["close"] for b in bars]
    assert ema(closes, 20) > 2050
    assert 0 <= rsi(closes, 14) <= 100
    assert atr(bars, 14) > 0
    assert regime(bars) == "TREND"
    structure_result = structure(bars)
    assert set(structure_result) == {"swing_highs", "swing_lows", "fvg"}


def test_xau_feature_contract_is_research_only():
    result = features(_bars())
    assert result["asset"] == "XAUUSD"
    assert result["research_only"] is True
    assert result["live_execution"] is False
    assert result["ema_20"] is not None


def test_xau_features_require_enough_data():
    try:
        features(_bars(10))
    except ValueError:
        return
    raise AssertionError("short XAU input must fail closed")
