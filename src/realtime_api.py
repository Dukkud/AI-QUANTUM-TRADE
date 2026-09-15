"""v31.3 realtime training API surface.

Market-data/training only. This module deliberately has no order-placement API.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.realtime_market import MarketTick

TIMEFRAMES = ("1M", "5M", "15M", "30M", "1H", "2H", "4H", "1D", "1W")
ASSETS = ("BTCUSDT", "XAUUSD")
AGENTS = tuple(f"Q{i}" for i in range(1, 9))


def realtime_policy() -> dict[str, Any]:
    return {
        "version": "31.3",
        "mode": "TRAINING_ONLY",
        "execution": "PAPER_ONLY",
        "live_orders": False,
        "assets": list(ASSETS),
        "timeframes": list(TIMEFRAMES),
        "agents": list(AGENTS),
        "latency_model": {
            "exchange_timestamp": "required_when_provider_supplies_it",
            "receive_timestamp": "captured_locally",
            "decision_latency": "measured_by_runtime",
            "execution_latency": "simulated_until_live_gate_is_open",
            "slippage": "simulated_and_recorded",
            "live_difference_warning": "Live execution may differ by milliseconds or more."
        },
    }


def normalize_tick(tick: MarketTick) -> dict[str, Any]:
    """Return an audit-friendly tick envelope for the training journal."""
    d = tick.to_dict()
    d["training_policy"] = "REALTIME_MARKET_DATA != LIVE_EXECUTION"
    d["captured_at_utc"] = datetime.now(timezone.utc).isoformat()
    return d


def source_status() -> dict[str, Any]:
    """Static capability declaration; it does not claim external connectivity."""
    return {
        "binance": {"market_data": True, "websocket": True, "orders": False},
        "mt5": {"market_data": True, "ticks": True, "orders": False},
        "ccxt": {"exchange_adapters": True, "orders_enabled": False},
        "yahoo": {"role": "reference/macro", "orders": False},
        "coincap": {"role": "reference", "orders": False},
        "external_connection_verified_in_deployment": False,
    }
