"""Deterministic market-data contract and replay foundation for AI-QUANTUM.

This module is deliberately strategy-neutral. It validates versioned OHLCV/quote
observations, produces a reproducible dataset fingerprint, and replays bars in
strict timestamp order. It does not fetch external data and cannot place orders.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from math import isfinite
from typing import Iterable, Mapping, Sequence

TIMEFRAME_MS = {
    "1M": 60_000, "5M": 300_000, "15M": 900_000, "30M": 1_800_000,
    "1H": 3_600_000, "2H": 7_200_000, "4H": 14_400_000,
    "1D": 86_400_000, "1W": 604_800_000,
}

@dataclass(frozen=True)
class MarketBar:
    timestamp_ms: int
    asset: str
    timeframe: str
    open: float
    high: float
    low: float
    close: float
    volume: float | None = None
    bid: float | None = None
    ask: float | None = None

    def as_dict(self) -> dict[str, object]:
        return {
            "timestamp_ms": self.timestamp_ms, "asset": self.asset,
            "timeframe": self.timeframe, "open": self.open, "high": self.high,
            "low": self.low, "close": self.close, "volume": self.volume,
            "bid": self.bid, "ask": self.ask,
        }

def coerce_bar(row: Mapping[str, object]) -> MarketBar:
    return MarketBar(
        timestamp_ms=int(row["timestamp_ms"]), asset=str(row["asset"]),
        timeframe=str(row["timeframe"]), open=float(row["open"]),
        high=float(row["high"]), low=float(row["low"]), close=float(row["close"]),
        volume=float(row["volume"]) if row.get("volume") is not None else None,
        bid=float(row["bid"]) if row.get("bid") is not None else None,
        ask=float(row["ask"]) if row.get("ask") is not None else None,
    )

def validate_dataset(rows: Iterable[Mapping[str, object] | MarketBar]) -> dict[str, object]:
    """Validate one asset/timeframe sequence without silently repairing data."""
    bars = [x if isinstance(x, MarketBar) else coerce_bar(x) for x in rows]
    errors: list[str] = []
    gaps: list[dict[str, int]] = []
    if not bars:
        return {"valid": False, "bars": 0, "errors": ["dataset is empty"], "gaps": gaps}
    asset, timeframe = bars[0].asset, bars[0].timeframe
    expected = TIMEFRAME_MS.get(timeframe)
    previous_ts: int | None = None
    seen: set[int] = set()
    for index, bar in enumerate(bars):
        prefix = f"bar[{index}]"
        if bar.asset != asset: errors.append(f"{prefix}: mixed assets")
        if bar.timeframe != timeframe: errors.append(f"{prefix}: mixed timeframes")
        prices = (bar.open, bar.high, bar.low, bar.close)
        if any(not isfinite(x) or x <= 0 for x in prices):
            errors.append(f"{prefix}: prices must be finite and positive")
        if bar.high < max(bar.open, bar.close) or bar.low > min(bar.open, bar.close) or bar.high < bar.low:
            errors.append(f"{prefix}: invalid OHLC relationship")
        if bar.volume is not None and (not isfinite(bar.volume) or bar.volume < 0):
            errors.append(f"{prefix}: invalid volume")
        if bar.bid is not None and (not isfinite(bar.bid) or bar.bid <= 0):
            errors.append(f"{prefix}: invalid bid")
        if bar.ask is not None and (not isfinite(bar.ask) or bar.ask <= 0):
            errors.append(f"{prefix}: invalid ask")
        if bar.bid is not None and bar.ask is not None and bar.ask < bar.bid:
            errors.append(f"{prefix}: ask below bid")
        if bar.timestamp_ms in seen: errors.append(f"{prefix}: duplicate timestamp")
        seen.add(bar.timestamp_ms)
        if previous_ts is not None:
            delta = bar.timestamp_ms - previous_ts
            if delta <= 0: errors.append(f"{prefix}: timestamps must be strictly increasing")
            elif expected is not None and delta != expected:
                gaps.append({"from_timestamp_ms": previous_ts, "to_timestamp_ms": bar.timestamp_ms, "delta_ms": delta})
        previous_ts = bar.timestamp_ms
    return {
        "valid": not errors, "bars": len(bars), "asset": asset, "timeframe": timeframe,
        "errors": errors, "gaps": gaps, "first_timestamp_ms": bars[0].timestamp_ms,
        "last_timestamp_ms": bars[-1].timestamp_ms,
        "native_quotes": all(bar.bid is not None and bar.ask is not None for bar in bars),
    }

def dataset_fingerprint(rows: Sequence[Mapping[str, object] | MarketBar]) -> str:
    """Return a stable SHA-256 fingerprint for the exact normalized dataset."""
    bars = [x if isinstance(x, MarketBar) else coerce_bar(x) for x in rows]
    canonical = json.dumps([bar.as_dict() for bar in bars], sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return sha256(canonical).hexdigest()

def replay(rows: Sequence[Mapping[str, object] | MarketBar]) -> list[dict[str, object]]:
    """Replay validated bars deterministically; no strategy or order execution."""
    bars = [x if isinstance(x, MarketBar) else coerce_bar(x) for x in rows]
    validation = validate_dataset(bars)
    if not validation["valid"]:
        raise ValueError("dataset validation failed: " + "; ".join(validation["errors"]))
    fingerprint = dataset_fingerprint(bars)
    events: list[dict[str, object]] = []
    previous_close: float | None = None
    for sequence, bar in enumerate(bars, start=1):
        events.append({
            "sequence": sequence, "timestamp_ms": bar.timestamp_ms, "asset": bar.asset,
            "timeframe": bar.timeframe, "open": bar.open, "high": bar.high,
            "low": bar.low, "close": bar.close, "previous_close": previous_close,
            "dataset_fingerprint": fingerprint, "research_only": True, "live_execution": False,
        })
        previous_close = bar.close
    return events
