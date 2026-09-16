"""Research-only XAUUSD multi-source adapters.

Gold API supplies keyless XAU/USD spot. Yahoo Finance supplies XAUUSD=X chart data.
The module never creates synthetic prices and never changes agent weights or live gates.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import json
from typing import Any
from urllib.parse import quote
from urllib.request import Request, urlopen


GOLD_API_BASE = "https://api.gold-api.com"
YAHOO_CHART_BASE = "https://query1.finance.yahoo.com/v8/finance/chart"
YAHOO_SYMBOL = "XAUUSD=X"


class XAUDataError(RuntimeError):
    pass


@dataclass(frozen=True)
class XAUQuote:
    source: str
    symbol: str
    price: float
    currency: str
    source_timestamp: str | None
    received_at: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _get_json(url: str, timeout: float = 10.0) -> dict[str, Any]:
    req = Request(url, headers={"User-Agent": "AI-QUANTUM-TRADE/34.5"})
    try:
        with urlopen(req, timeout=timeout) as response:
            if getattr(response, "status", 200) != 200:
                raise XAUDataError(f"HTTP {getattr(response, 'status', 'unknown')} from {url}")
            return json.loads(response.read().decode("utf-8"))
    except XAUDataError:
        raise
    except Exception as exc:
        raise XAUDataError(f"request failed for {url}: {exc}") from exc


def fetch_gold_api_quote(timeout: float = 10.0) -> XAUQuote:
    data = _get_json(f"{GOLD_API_BASE}/price/XAU", timeout)
    price = float(data.get("price"))
    if price <= 0:
        raise XAUDataError("Gold API returned non-positive XAU price")
    return XAUQuote(
        source="GOLD_API",
        symbol=str(data.get("symbol", "XAU")),
        price=price,
        currency=str(data.get("currency", "USD")),
        source_timestamp=data.get("updatedAt") or data.get("timestamp"),
        received_at=datetime.now(timezone.utc).isoformat(),
    )


def _period_seconds(period: str) -> int:
    units = {"1m": 60, "5m": 300, "15m": 900, "30m": 1800, "1h": 3600, "2h": 7200, "4h": 14400, "1d": 86400, "1wk": 604800}
    if period not in units:
        raise XAUDataError(f"unsupported Yahoo interval: {period}")
    return units[period]


def fetch_yahoo_xauusd(interval: str = "1h", bars: int = 500, timeout: float = 10.0) -> dict[str, Any]:
    if bars < 1 or bars > 5000:
        raise XAUDataError("bars must be between 1 and 5000")
    _period_seconds(interval)
    period2 = int(datetime.now(timezone.utc).timestamp())
    period1 = period2 - bars * _period_seconds(interval) * 2
    url = (f"{YAHOO_CHART_BASE}/{quote(YAHOO_SYMBOL, safe='')}"
           f"?period1={period1}&period2={period2}&interval={interval}&events=history&includeAdjustedClose=true")
    data = _get_json(url, timeout)
    result = (data.get("chart", {}).get("result") or [None])[0]
    if not result:
        raise XAUDataError("Yahoo Finance returned no chart result")
    timestamps = result.get("timestamp") or []
    q = result.get("indicators", {}).get("quote", [{}])[0]
    rows: list[dict[str, Any]] = []
    for i, ts in enumerate(timestamps):
        vals = {k: (q.get(k) or [None] * len(timestamps))[i] for k in ("open", "high", "low", "close", "volume")}
        if any(vals[k] is None for k in ("open", "high", "low", "close")):
            continue
        if any(float(vals[k]) <= 0 for k in ("open", "high", "low", "close")):
            raise XAUDataError("Yahoo Finance returned non-positive OHLC")
        rows.append({"timestamp": datetime.fromtimestamp(int(ts), tz=timezone.utc).isoformat(), "timeframe": interval, **{k: float(v) for k, v in vals.items() if v is not None}})
    if not rows:
        raise XAUDataError("Yahoo Finance returned no valid OHLC rows")
    return {"source": "YAHOO_FINANCE", "symbol": YAHOO_SYMBOL, "interval": interval, "rows": rows[-bars:], "raw_meta": result.get("meta", {})}


def compare_spot(gold: XAUQuote, yahoo_last: float) -> dict[str, Any]:
    if gold.price <= 0 or yahoo_last <= 0:
        raise XAUDataError("prices must be positive")
    basis = gold.price / yahoo_last - 1.0
    return {"gold_api": gold.as_dict(), "yahoo_last": yahoo_last, "basis_pct": basis * 100.0, "decision": "EVIDENCE_ONLY", "research_only": True, "weight_update": False, "live_execution": False}
