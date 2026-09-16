import json
from unittest.mock import patch

from src.xau_multi_source import XAUDataError, fetch_gold_api_quote, fetch_yahoo_xauusd, compare_spot


class FakeResponse:
    status = 200
    def __init__(self, payload): self.payload = json.dumps(payload).encode()
    def read(self): return self.payload
    def __enter__(self): return self
    def __exit__(self, *args): return False


def test_gold_api_quote_parsing():
    payload = {"symbol": "XAU", "name": "Gold", "price": 4300.5, "currency": "USD", "updatedAt": "2026-09-16T09:00:00Z"}
    with patch("src.xau_multi_source.urlopen", return_value=FakeResponse(payload)):
        q = fetch_gold_api_quote()
    assert q.source == "GOLD_API"
    assert q.price == 4300.5
    assert q.currency == "USD"


def test_yahoo_chart_parsing():
    payload = {"chart": {"result": [{"timestamp": [1000, 4600], "indicators": {"quote": [{"open": [1, 2], "high": [2, 3], "low": [0.5, 1.5], "close": [1.5, 2.5], "volume": [10, 11]}]}, "meta": {"symbol": "XAUUSD=X"}}], "error": None}}
    with patch("src.xau_multi_source.urlopen", return_value=FakeResponse(payload)):
        result = fetch_yahoo_xauusd("1h", 2)
    assert result["source"] == "YAHOO_FINANCE"
    assert len(result["rows"]) == 2
    assert result["rows"][-1]["close"] == 2.5


def test_invalid_yahoo_interval_fails_closed():
    try:
        fetch_yahoo_xauusd("2h", 10)
        assert False, "expected XAUDataError"
    except XAUDataError as exc:
        assert "unsupported Yahoo interval" in str(exc)


def test_spot_comparison_is_evidence_only():
    payload = {"symbol": "XAU", "price": 4300.0, "currency": "USD"}
    with patch("src.xau_multi_source.urlopen", return_value=FakeResponse(payload)):
        q = fetch_gold_api_quote()
    result = compare_spot(q, 4299.0)
    assert result["research_only"] is True
    assert result["weight_update"] is False
    assert result["live_execution"] is False
    assert result["decision"] == "EVIDENCE_ONLY"
