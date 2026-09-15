"""CCXT unified market-data adapter for paper training.

The adapter intentionally exposes public market data only. It does not create
orders. Exchange credentials are not required for public feeds and must never
be committed to Git.
"""
from __future__ import annotations

import time
from typing import Optional

from src.realtime_market import MarketTick


class CCXTMarketAdapter:
    def __init__(self, exchange_id: str = "binance", symbol: str = "BTC/USDT") -> None:
        import ccxt
        if not hasattr(ccxt, exchange_id):
            raise ValueError(f"Unsupported CCXT exchange: {exchange_id}")
        self.exchange_id = exchange_id
        self.symbol = symbol
        self.exchange = getattr(ccxt, exchange_id)({"enableRateLimit": True})

    def ticker(self) -> MarketTick:
        t = self.exchange.fetch_ticker(self.symbol)
        now = time.time_ns() // 1_000_000
        ts = t.get("timestamp")
        return MarketTick(
            venue=f"ccxt:{self.exchange_id}",
            symbol=self.symbol,
            bid=float(t["bid"]) if t.get("bid") is not None else None,
            ask=float(t["ask"]) if t.get("ask") is not None else None,
            last=float(t["last"]) if t.get("last") is not None else None,
            volume=float(t["baseVolume"]) if t.get("baseVolume") is not None else None,
            exchange_ts_ms=int(ts) if ts is not None else None,
            received_ts_ms=now,
            stream="ticker",
        )

    def orderbook(self, limit: int = 20) -> dict:
        """Public order book for model features; never submits an order."""
        return self.exchange.fetch_order_book(self.symbol, limit=limit)
