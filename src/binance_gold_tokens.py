"""v34.3 Binance gold-token research adapter.

PAXGUSDT and XAUTUSDT are treated as market-data/evidence sources only.
No account credentials, order endpoints, or execution paths are used.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Any, Callable

import requests

BINANCE_SPOT = "https://api.binance.com"
ASSET_SYMBOLS = {"PAXG": "PAXGUSDT", "XAUT": "XAUTUSDT"}
INTERVALS = {"1M": "1m", "5M": "5m", "15M": "15m", "30M": "30m", "1H": "1h", "2H": "2h", "4H": "4h", "1D": "1d", "1W": "1w"}


class BinanceGoldError(RuntimeError):
    pass


@dataclass(frozen=True)
class BinanceGoldConfig:
    base_url: str = BINANCE_SPOT
    timeout_seconds: float = 10.0
    max_bars: int = 500


class BinanceGoldClient:
    """Public Binance Spot market-data client. No API key is required."""

    def __init__(self, config: BinanceGoldConfig | None = None, session: Any = None):
        self.config = config or BinanceGoldConfig()
        self.session = session or requests.Session()

    def _get(self, path: str, params: dict[str, Any]) -> Any:
        try:
            response = self.session.get(f"{self.config.base_url}{path}", params=params, timeout=self.config.timeout_seconds)
            response.raise_for_status()
            return response.json()
        except Exception as exc:  # requests + transport errors are fail-closed
            raise BinanceGoldError(f"Binance market-data request failed: {exc}") from exc

    def exchange_symbols(self) -> set[str]:
        payload = self._get("/api/v3/exchangeInfo", {})
        return {str(row.get("symbol", "")) for row in payload.get("symbols", []) if row.get("status") == "TRADING"}

    def resolve_symbol(self, asset: str) -> str:
        asset = asset.upper()
        symbol = ASSET_SYMBOLS.get(asset)
        if not symbol:
            raise BinanceGoldError(f"unsupported gold token: {asset}")
        symbols = self.exchange_symbols()
        if symbol not in symbols:
            raise BinanceGoldError(f"Binance symbol not currently tradable: {symbol}")
        return symbol

    def klines(self, asset: str, timeframe: str = "1H", limit: int = 200) -> list[dict[str, Any]]:
        timeframe = timeframe.upper()
        if timeframe not in INTERVALS:
            raise BinanceGoldError(f"unsupported timeframe: {timeframe}")
        limit = max(2, min(int(limit), self.config.max_bars))
        symbol = self.resolve_symbol(asset)
        rows = self._get("/api/v3/klines", {"symbol": symbol, "interval": INTERVALS[timeframe], "limit": limit})
        normalized: list[dict[str, Any]] = []
        for row in rows:
            if len(row) < 12:
                raise BinanceGoldError("Binance kline row has an invalid schema")
            normalized.append({
                "timestamp": int(row[0]), "open": float(row[1]), "high": float(row[2]),
                "low": float(row[3]), "close": float(row[4]), "volume": float(row[5]),
                "close_timestamp": int(row[6]), "quote_volume": float(row[7]),
                "trades": int(row[8]), "taker_buy_volume": float(row[9]),
                "taker_buy_quote_volume": float(row[10]),
            })
        self._validate(normalized)
        return normalized

    @staticmethod
    def _validate(rows: list[dict[str, Any]]) -> None:
        timestamps = [r["timestamp"] for r in rows]
        if timestamps != sorted(set(timestamps)):
            raise BinanceGoldError("Binance klines contain duplicate or non-monotonic timestamps")
        for row in rows:
            if not (row["low"] <= row["open"] <= row["high"] and row["low"] <= row["close"] <= row["high"]):
                raise BinanceGoldError("Binance kline violates OHLC integrity")
            if row["volume"] < 0 or row["trades"] < 0:
                raise BinanceGoldError("Binance kline contains negative activity")

    @staticmethod
    def _ema(values: list[float], period: int) -> float | None:
        if len(values) < period:
            return None
        alpha = 2.0 / (period + 1.0)
        value = sum(values[:period]) / period
        for item in values[period:]:
            value = alpha * item + (1.0 - alpha) * value
        return value

    @staticmethod
    def _rsi(values: list[float], period: int = 14) -> float | None:
        if len(values) <= period:
            return None
        gains: list[float] = []
        losses: list[float] = []
        for a, b in zip(values[-period - 1:-1], values[-period:]):
            change = b - a
            gains.append(max(change, 0.0)); losses.append(max(-change, 0.0))
        avg_gain = sum(gains) / period; avg_loss = sum(losses) / period
        if avg_loss == 0:
            return 100.0 if avg_gain > 0 else 50.0
        rs = avg_gain / avg_loss
        return 100.0 - (100.0 / (1.0 + rs))

    @staticmethod
    def _atr(rows: list[dict[str, Any]], period: int = 14) -> float | None:
        if len(rows) <= period:
            return None
        trs: list[float] = []
        previous = rows[0]["close"]
        for row in rows[1:]:
            trs.append(max(row["high"] - row["low"], abs(row["high"] - previous), abs(row["low"] - previous)))
            previous = row["close"]
        return sum(trs[-period:]) / period

    def analyze(self, asset: str, timeframe: str = "1H", limit: int = 200) -> dict[str, Any]:
        rows = self.klines(asset, timeframe, limit)
        closes = [r["close"] for r in rows]
        latest = rows[-1]
        ema20 = self._ema(closes, 20); ema50 = self._ema(closes, 50)
        rsi = self._rsi(closes); atr = self._atr(rows)
        trend = "UNKNOWN"
        if ema20 is not None and ema50 is not None:
            if latest["close"] > ema20 > ema50: trend = "UP"
            elif latest["close"] < ema20 < ema50: trend = "DOWN"
            else: trend = "RANGE_TRANSITION"
        return {
            "asset": asset.upper(), "symbol": self.resolve_symbol(asset), "source": "BINANCE_SPOT",
            "timeframe": timeframe.upper(), "latest": latest, "indicators": {"ema20": ema20, "ema50": ema50, "rsi14": rsi, "atr14": atr},
            "regime_hint": trend, "bars": len(rows), "research_only": True, "live_execution": False,
        }


def build_metals_block(
    client: BinanceGoldClient,
    timeframe: str = "1H",
    limit: int = 200,
    xauusd: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build one precious-metals block with separate token-button payloads.

    XAUUSD is supplied by an existing/independent source; it is never fabricated
    from Binance PAXG/XAUT. Missing XAUUSD is reported explicitly.
    """
    tokens: dict[str, Any] = {}
    for asset in ("PAXG", "XAUT"):
        try:
            tokens[asset] = client.analyze(asset, timeframe, limit)
        except BinanceGoldError as exc:
            tokens[asset] = {"asset": asset, "ok": False, "error": str(exc), "research_only": True, "live_execution": False}
        else:
            tokens[asset]["ok"] = True
    return {
        "block": "GOLD_DIGITAL_METALS",
        "timeframe": timeframe.upper(),
        "xauusd": xauusd if xauusd is not None else {"available": False, "reason": "XAUUSD must come from an independent source"},
        "tokens": tokens,
        "ui": {"buttons": [{"id": "xauusd", "label": "XAUUSD"}, {"id": "paxg", "label": "PAXG"}, {"id": "xaut", "label": "XAUT"}]},
        "policy": {"research_only": True, "live_execution": False, "orders": False},
    }
