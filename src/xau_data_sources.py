"""XAUUSD external data sources and reconciliation.

Gold API supplies spot gold (XAU/USD). Yahoo Finance supplies COMEX gold
futures (GC=F). They are deliberately kept as separate market instruments:
spot is not silently treated as futures and vice versa.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import json
import time
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

GOLD_API_BASE = "https://api.gold-api.com"
YAHOO_CHART_BASE = "https://query1.finance.yahoo.com/v8/finance/chart"
YAHOO_SYMBOL = "GC=F"


@dataclass(frozen=True)
class PriceSnapshot:
    source: str
    instrument: str
    symbol: str
    price: float
    currency: str
    updated_at_utc: str
    fetched_at_utc: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SourceUnavailable(RuntimeError):
    pass


def _get_json(url: str, params: dict[str, Any] | None = None, *, timeout: float = 10.0) -> Any:
    if params:
        url = f"{url}?{urlencode(params)}"
    request = Request(
        url,
        headers={
            "User-Agent": "AI-QUANTUM-TRADE/1.0",
            "Accept": "application/json",
        },
        method="GET",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        raise SourceUnavailable(f"GET failed for {url}: {exc}") from exc


def fetch_gold_api_xau() -> PriceSnapshot:
    data = _get_json(f"{GOLD_API_BASE}/price/XAU")
    price = float(data["price"])
    updated = data.get("updatedAt") or datetime.now(timezone.utc).isoformat()
    return PriceSnapshot(
        source="gold-api.com",
        instrument="XAUUSD_SPOT",
        symbol="XAU",
        price=price,
        currency=str(data.get("currency", "USD")),
        updated_at_utc=updated,
        fetched_at_utc=datetime.now(timezone.utc).isoformat(),
    )


def fetch_yahoo_gc_f() -> PriceSnapshot:
    data = _get_json(
        f"{YAHOO_CHART_BASE}/{YAHOO_SYMBOL}",
        {"range": "1d", "interval": "1m", "events": "div,splits"},
    )
    result = (data.get("chart") or {}).get("result") or []
    if not result:
        error = (data.get("chart") or {}).get("error")
        raise SourceUnavailable(f"Yahoo Finance returned no result: {error}")
    item = result[0]
    meta = item.get("meta") or {}
    price = meta.get("regularMarketPrice")
    if price is None:
        closes = ((item.get("indicators") or {}).get("quote") or [{}])[0].get("close") or []
        price = next((v for v in reversed(closes) if v is not None), None)
    if price is None:
        raise SourceUnavailable("Yahoo Finance GC=F has no current price")
    market_time = meta.get("regularMarketTime")
    updated = datetime.fromtimestamp(market_time, tz=timezone.utc).isoformat() if market_time else datetime.now(timezone.utc).isoformat()
    return PriceSnapshot(
        source="yahoo-finance",
        instrument="XAUUSD_FUTURES",
        symbol=YAHOO_SYMBOL,
        price=float(price),
        currency=str(meta.get("currency", "USD")),
        updated_at_utc=updated,
        fetched_at_utc=datetime.now(timezone.utc).isoformat(),
    )


def reconcile_xauusd(max_age_seconds: int = 120) -> dict[str, Any]:
    """Fetch both sources and return a non-authoritative reconciliation.

    The two sources represent different instruments. The spread is therefore
    a diagnostic basis/market-difference measure, not a price-error metric.
    """
    snapshots: list[PriceSnapshot] = []
    errors: dict[str, str] = {}
    for name, fetcher in (("gold_api", fetch_gold_api_xau), ("yahoo_gc_f", fetch_yahoo_gc_f)):
        try:
            snapshots.append(fetcher())
        except SourceUnavailable as exc:
            errors[name] = str(exc)

    result: dict[str, Any] = {
        "asset": "XAUUSD",
        "status": "DEGRADED" if errors else "OK",
        "sources": [s.to_dict() for s in snapshots],
        "errors": errors,
        "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    if len(snapshots) == 2:
        spot, futures = snapshots
        result["futures_minus_spot"] = futures.price - spot.price
        result["futures_minus_spot_pct"] = ((futures.price / spot.price) - 1.0) * 100.0
        result["source_age_seconds"] = {
            "gold_api": max(0.0, time.time() - datetime.fromisoformat(spot.updated_at_utc.replace("Z", "+00:00")).timestamp()),
            "yahoo_gc_f": max(0.0, time.time() - datetime.fromisoformat(futures.updated_at_utc.replace("Z", "+00:00")).timestamp()),
        }
        result["fresh"] = all(age <= max_age_seconds for age in result["source_age_seconds"].values())
    else:
        result["fresh"] = False
    return result
