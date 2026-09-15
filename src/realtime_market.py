"""Realtime market-data adapters for AI-QUANTUM training.

IMPORTANT: this module is deliberately market-data/paper-only. It never places
orders. Credentials, if later configured, must be supplied outside source control.
"""
from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass, asdict
from typing import AsyncIterator, Optional

import requests


@dataclass(frozen=True)
class MarketTick:
    venue: str
    symbol: str
    bid: Optional[float]
    ask: Optional[float]
    last: Optional[float]
    volume: Optional[float]
    exchange_ts_ms: Optional[int]
    received_ts_ms: int
    stream: str
    training_only: bool = True

    @property
    def feed_latency_ms(self) -> Optional[int]:
        if self.exchange_ts_ms is None:
            return None
        return self.received_ts_ms - self.exchange_ts_ms

    def to_dict(self) -> dict:
        d = asdict(self)
        d["feed_latency_ms"] = self.feed_latency_ms
        return d


class BinancePublicWS:
    """Binance public aggTrade stream, normalized to MarketTick.

    Uses the lightweight `websockets` package directly so the training feed is
    independent of exchange credentials. No order/trading endpoint is exposed.
    """

    def __init__(self, symbol: str = "btcusdt") -> None:
        self.symbol = symbol.lower()
        self.url = f"wss://stream.binance.com:9443/ws/{self.symbol}@aggTrade"

    async def stream(self) -> AsyncIterator[MarketTick]:
        import websockets

        backoff = 1.0
        while True:
            try:
                async with websockets.connect(self.url, ping_interval=20, ping_timeout=20) as ws:
                    backoff = 1.0
                    async for raw in ws:
                        now = time.time_ns() // 1_000_000
                        msg = json.loads(raw)
                        yield MarketTick(
                            venue="binance",
                            symbol=self.symbol.upper(),
                            bid=None,
                            ask=None,
                            last=float(msg["p"]),
                            volume=float(msg["q"]),
                            exchange_ts_ms=int(msg["T"]),
                            received_ts_ms=now,
                            stream="aggTrade",
                        )
            except Exception:
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2.0, 30.0)


class BinanceRestSnapshot:
    """Small REST snapshot for startup/recovery validation."""

    def __init__(self, symbol: str = "BTCUSDT") -> None:
        self.symbol = symbol.upper()

    def ticker(self) -> dict:
        r = requests.get(
            "https://api.binance.com/api/v3/ticker/bookTicker",
            params={"symbol": self.symbol},
            timeout=10,
        )
        r.raise_for_status()
        return r.json()


class MT5MarketData:
    """Optional MT5 market-data adapter. It cannot place orders."""

    def __init__(self, symbol: str = "XAUUSD") -> None:
        self.symbol = symbol
        self._mt5 = None

    def initialize(self, path: str | None = None) -> bool:
        try:
            import MetaTrader5 as mt5
        except ImportError:
            return False
        self._mt5 = mt5
        return bool(mt5.initialize(path) if path else mt5.initialize())

    def tick(self) -> Optional[MarketTick]:
        if self._mt5 is None:
            return None
        t = self._mt5.symbol_info_tick(self.symbol)
        if t is None:
            return None
        now = time.time_ns() // 1_000_000
        return MarketTick(
            venue="mt5",
            symbol=self.symbol,
            bid=float(t.bid),
            ask=float(t.ask),
            last=float(t.last or 0.0) or None,
            volume=float(t.volume),
            exchange_ts_ms=int(t.time_msc),
            received_ts_ms=now,
            stream="symbol_info_tick",
        )

    def shutdown(self) -> None:
        if self._mt5 is not None:
            self._mt5.shutdown()
