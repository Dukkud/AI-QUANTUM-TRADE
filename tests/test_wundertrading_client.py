import base64
import hashlib
import hmac

from src.wundertrading_client import WunderTradingClient


def test_hmac_payload_contract(monkeypatch):
    client = WunderTradingClient("api", "secret", recv_window_ms=60000)
    captured = {}

    class DummyResponse:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False
        def read(self):
            return b'{"ok": true}'

    def fake_urlopen(request, timeout=15):
        captured["headers"] = dict(request.headers)
        captured["url"] = request.full_url
        return DummyResponse()

    monkeypatch.setattr("src.wundertrading_client.urlopen", fake_urlopen)
    monkeypatch.setattr("src.wundertrading_client.time.time", lambda: 1770990729.0)

    result = client.api_profiles()
    assert result["ok"] is True
    timestamp = "1770990729000"
    path = "/open_api/api_profiles"
    payload = "\n".join(["GET", path, timestamp, "60000", ""])
    expected = base64.b64encode(
        hmac.new(b"secret", payload.encode(), hashlib.sha256).digest()
    ).decode()
    assert captured["headers"]["X-api-key"] == "api"
    assert captured["headers"]["X-signature"] == expected
    assert captured["headers"]["X-timestamp"] == timestamp


def test_order_history_validates_id_and_limit():
    client = WunderTradingClient("api", "secret")
    try:
        client.strategy_orders_history("", 1, 100)
        assert False
    except ValueError as exc:
        assert "profile_strategy_id" in str(exc)
    try:
        client.strategy_orders_history("abc", 1, 101)
        assert False
    except ValueError as exc:
        assert "limit" in str(exc)
