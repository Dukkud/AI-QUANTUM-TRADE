from src.xau_data_sources import PriceSnapshot


def test_price_snapshot_contract():
    s = PriceSnapshot(
        source="gold-api.com",
        instrument="XAUUSD_SPOT",
        symbol="XAU",
        price=4200.0,
        currency="USD",
        updated_at_utc="2026-09-16T00:00:00+00:00",
        fetched_at_utc="2026-09-16T00:00:01+00:00",
    )
    assert s.to_dict()["instrument"] == "XAUUSD_SPOT"
    assert s.to_dict()["price"] == 4200.0


def test_yahoo_is_explicitly_futures_symbol():
    from src.xau_data_sources import YAHOO_SYMBOL
    assert YAHOO_SYMBOL == "GC=F"
