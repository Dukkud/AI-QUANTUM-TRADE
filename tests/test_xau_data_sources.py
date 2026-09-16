import json
from datetime import datetime, timezone

import src.xau_data_sources as m


class Response:
    def __init__(self, payload):
        self._body = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self._body


def test_price_snapshot_contract():
    snapshot = m.PriceSnapshot(
        source="gold-api.com",
        instrument="XAUUSD_SPOT",
        symbol="XAU",
        price=4200.0,
        currency="USD",
        updated_at_utc="2026-09-16T00:00:00+00:00",
        fetched_at_utc="2026-09-16T00:00:01+00:00",
    )
    assert snapshot.to_dict()["instrument"] == "XAUUSD_SPOT"
    assert snapshot.to_dict()["price"] == 4200.0


def test_yahoo_is_explicitly_futures_symbol():
    assert m.YAHOO_SYMBOL == "GC=F"


def test_gold_api_payload_is_parsed(monkeypatch):
    monkeypatch.setattr(
        m,
        "urlopen",
        lambda request, timeout=10.0: Response(
            {
                "price": 4210.5,
                "currency": "USD",
                "updatedAt": "2026-09-16T10:00:00Z",
            }
        ),
    )
    snapshot = m.fetch_gold_api_xau()
    assert snapshot.instrument == "XAUUSD_SPOT"
    assert snapshot.price == 4210.5
    assert snapshot.updated_at_utc == "2026-09-16T10:00:00+00:00"


def test_yahoo_payload_is_parsed(monkeypatch):
    market_time = datetime(2026, 9, 16, 10, tzinfo=timezone.utc).timestamp()
    monkeypatch.setattr(
        m,
        "urlopen",
        lambda request, timeout=10.0: Response(
            {
                "chart": {
                    "result": [
                        {
                            "meta": {
                                "regularMarketPrice": 4230.0,
                                "currency": "USD",
                                "regularMarketTime": market_time,
                            }
                        }
                    ]
                }
            }
        ),
    )
    snapshot = m.fetch_yahoo_gc_f()
    assert snapshot.instrument == "XAUUSD_FUTURES"
    assert snapshot.symbol == "GC=F"
    assert snapshot.price == 4230.0


def test_reconcile_does_not_average_spot_and_futures(monkeypatch):
    reference_time = datetime(2026, 9, 16, 10, tzinfo=timezone.utc).timestamp()
    monkeypatch.setattr(m.time, "time", lambda: reference_time + 1.0)
    monkeypatch.setattr(
        m,
        "fetch_gold_api_xau",
        lambda: m.PriceSnapshot(
            "gold-api.com", "XAUUSD_SPOT", "XAU", 4200.0, "USD",
            "2026-09-16T10:00:00+00:00", "2026-09-16T10:00:01+00:00"
        ),
    )
    monkeypatch.setattr(
        m,
        "fetch_yahoo_gc_f",
        lambda: m.PriceSnapshot(
            "yahoo-finance", "XAUUSD_FUTURES", "GC=F", 4210.0, "USD",
            "2026-09-16T10:00:00+00:00", "2026-09-16T10:00:01+00:00"
        ),
    )
    result = m.reconcile_xauusd(max_age_seconds=120)
    assert result["status"] == "OK"
    assert result["fresh"] is True
    assert result["futures_minus_spot"] == 10.0
    assert result["futures_minus_spot_pct"] > 0
    assert len(result["sources"]) == 2


def test_reconcile_degrades_when_source_fails(monkeypatch):
    monkeypatch.setattr(
        m,
        "fetch_gold_api_xau",
        lambda: (_ for _ in ()).throw(m.SourceUnavailable("gold api down")),
    )
    monkeypatch.setattr(
        m,
        "fetch_yahoo_gc_f",
        lambda: m.PriceSnapshot(
            "yahoo-finance", "XAUUSD_FUTURES", "GC=F", 4210.0, "USD",
            "2026-09-16T10:00:00+00:00", "2026-09-16T10:00:01+00:00"
        ),
    )
    result = m.reconcile_xauusd()
    assert result["status"] == "DEGRADED"
    assert result["fresh"] is False
    assert "gold_api" in result["errors"]


def test_reconcile_degrades_when_source_is_stale(monkeypatch):
    old = "2020-01-01T00:00:00+00:00"
    monkeypatch.setattr(
        m,
        "fetch_gold_api_xau",
        lambda: m.PriceSnapshot("gold-api.com", "XAUUSD_SPOT", "XAU", 4200.0, "USD", old, old),
    )
    monkeypatch.setattr(
        m,
        "fetch_yahoo_gc_f",
        lambda: m.PriceSnapshot("yahoo-finance", "XAUUSD_FUTURES", "GC=F", 4210.0, "USD", old, old),
    )
    result = m.reconcile_xauusd(max_age_seconds=120)
    assert result["fresh"] is False
    assert result["status"] == "DEGRADED"


def test_invalid_price_is_rejected(monkeypatch):
    monkeypatch.setattr(m, "urlopen", lambda request, timeout=10.0: Response({"price": 0}))
    try:
        m.fetch_gold_api_xau()
    except m.SourceUnavailable as exc:
        assert "non-positive" in str(exc)
    else:
        raise AssertionError("non-positive price must be rejected")
