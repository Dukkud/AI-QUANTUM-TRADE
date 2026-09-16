import os

import pytest

from src.tvremix_adapter import (
    DEFAULT_ENDPOINT,
    TVRemixClient,
    TVRemixConfig,
    TVRemixError,
    TVRemixValidator,
)


class FakeResponse:
    def __init__(self, payload, status=200, headers=None):
        self.status_code = status
        self.headers = {"content-type": "application/json", **(headers or {})}
        self.text = __import__("json").dumps(payload)

    def json(self):
        return __import__("json").loads(self.text)


def test_validator_accepts_clean_causal_ohlcv():
    rows = [
        {"timestamp": 1000, "open": 10, "high": 12, "low": 9, "close": 11, "volume": 5},
        {"timestamp": 1060, "open": 11, "high": 13, "low": 10, "close": 12, "volume": 6},
        {"timestamp": 1120, "open": 12, "high": 14, "low": 11, "close": 13, "volume": 7},
    ]
    result = TVRemixValidator.validate(rows, "OANDA:XAUUSD", "1M")
    assert result.valid is True
    assert result.rows == 3
    assert result.duplicates == 0
    assert result.non_monotonic == 0
    assert result.fingerprint


def test_validator_rejects_duplicate_and_bad_ohlc():
    rows = [
        {"timestamp": 1000, "open": 10, "high": 12, "low": 9, "close": 11},
        {"timestamp": 1000, "open": 20, "high": 15, "low": 19, "close": 21},
    ]
    result = TVRemixValidator.validate(rows, "BINANCE:BTCUSDT", "5M")
    assert result.valid is False
    assert result.duplicates == 1
    assert result.invalid_ohlc == 1


def test_client_discovers_tools_and_calls_ohlcv(monkeypatch):
    monkeypatch.setenv("TVREMIX_API_KEY", "tvr_test_only")
    calls = []

    def transport(url, headers, json, timeout):
        calls.append((url, headers, json))
        method = json["method"]
        if method == "initialize":
            return FakeResponse({"jsonrpc": "2.0", "id": json["id"], "result": {"protocolVersion": "2025-06-18"}}, headers={"Mcp-Session-Id": "test-session"})
        if method == "notifications/initialized":
            return FakeResponse({}, status=202)
        if method == "tools/list":
            return FakeResponse({"jsonrpc": "2.0", "id": json["id"], "result": {"tools": [{"name": "get_ohlcv"}]}})
        if method == "tools/call":
            return FakeResponse({"jsonrpc": "2.0", "id": json["id"], "result": {"data": [
                {"timestamp": 1000, "open": 10, "high": 12, "low": 9, "close": 11, "volume": 5},
                {"timestamp": 1060, "open": 11, "high": 13, "low": 10, "close": 12, "volume": 6},
                {"timestamp": 1120, "open": 12, "high": 14, "low": 11, "close": 13, "volume": 7},
            ]}})
        raise AssertionError(method)

    client = TVRemixClient(TVRemixConfig(endpoint=DEFAULT_ENDPOINT, api_key_present=True), transport=transport)
    result = client.get_ohlcv("OANDA:XAUUSD", "1M", 3)
    assert result["validation"]["valid"] is True
    assert result["validation"]["rows"] == 3
    assert client.status()["secret_exposed"] is False
    assert calls[0][1]["Authorization"] == "Bearer tvr_test_only"


def test_client_fails_closed_without_key(monkeypatch):
    monkeypatch.delenv("TVREMIX_API_KEY", raising=False)
    client = TVRemixClient(TVRemixConfig(api_key_present=False), transport=lambda *a, **k: None)
    with pytest.raises(TVRemixError, match="TVREMIX_API_KEY"):
        client.initialize()


def test_timeframes_are_bounded():
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setenv("TVREMIX_API_KEY", "tvr_test_only")
    try:
        client = TVRemixClient(TVRemixConfig(api_key_present=True), transport=lambda *a, **k: None)
        with pytest.raises(ValueError):
            client.get_ohlcv("OANDA:XAUUSD", "3M", 1)
    finally:
        monkeypatch.undo()
