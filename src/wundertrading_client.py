"""Read-only WunderTrading REST client for AI-QUANTUM evidence ingestion.

This module intentionally contains no order-placement methods. It is for
training/evidence collection only: profiles, live strategies and the last
three months of strategy history/orders exposed by WunderTrading.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE_URL = os.getenv("WUNDERTRADING_BASE_URL", "https://wundertrading.com")
API_KEY_ENV = "WUNDERTRADING_API_KEY"
API_SECRET_ENV = "WUNDERTRADING_API_SECRET"
RECV_WINDOW_MS = int(os.getenv("WUNDERTRADING_RECV_WINDOW_MS", "60000"))


class WunderTradingError(RuntimeError):
    pass


@dataclass(frozen=True)
class WunderTradingClient:
    api_key: str
    api_secret: str
    base_url: str = BASE_URL
    recv_window_ms: int = RECV_WINDOW_MS

    @classmethod
    def from_env(cls) -> "WunderTradingClient":
        key = os.getenv(API_KEY_ENV)
        secret = os.getenv(API_SECRET_ENV)
        if not key or not secret:
            raise WunderTradingError(
                f"Missing {API_KEY_ENV} or {API_SECRET_ENV}; configure them as runtime secrets."
            )
        return cls(key, secret)

    def _request(self, method: str, path: str, params: dict[str, Any] | None = None) -> Any:
        query = urlencode(params or {}, doseq=True)
        request_path = f"{path}?{query}" if query else path
        timestamp = str(int(time.time() * 1000))
        recv_window = str(self.recv_window_ms)
        body = ""
        payload = "\n".join([method.upper(), request_path, timestamp, recv_window, body])
        signature = base64.b64encode(
            hmac.new(self.api_secret.encode(), payload.encode(), hashlib.sha256).digest()
        ).decode()
        url = f"{self.base_url.rstrip('/')}{request_path}"
        request = Request(
            url,
            headers={
                "Accept": "application/json",
                "X-API-Key": self.api_key,
                "X-Signature": signature,
                "X-Timestamp": timestamp,
                "X-Recv-Window": recv_window,
                "User-Agent": "AI-QUANTUM-TRADE/1.0",
            },
            method=method.upper(),
        )
        try:
            with urlopen(request, timeout=15) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise WunderTradingError(f"WunderTrading request failed: {method} {path}: {exc}") from exc

    def api_profiles(self) -> Any:
        return self._request("GET", "/open_api/api_profiles")

    def live_strategies(self) -> Any:
        return self._request("GET", "/open_api/strategies/live")

    def strategy_history(self) -> Any:
        return self._request("GET", "/open_api/strategies/history")

    def strategy_orders_history(self, profile_strategy_id: str, page: int = 1, limit: int = 100) -> Any:
        if not profile_strategy_id:
            raise ValueError("profile_strategy_id is required")
        if not 1 <= page:
            raise ValueError("page must be >= 1")
        if not 1 <= limit <= 100:
            raise ValueError("limit must be between 1 and 100")
        return self._request(
            "GET",
            f"/open_api/strategies/history/orders/{profile_strategy_id}",
            {"page": page, "limit": limit},
        )


def collect_evidence() -> dict[str, Any]:
    """Collect read-only WunderTrading evidence for the training/audit layer."""
    client = WunderTradingClient.from_env()
    errors: dict[str, str] = {}
    result: dict[str, Any] = {"source": "wundertrading", "fetched_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    for name, getter in (
        ("api_profiles", client.api_profiles),
        ("live_strategies", client.live_strategies),
        ("strategy_history", client.strategy_history),
    ):
        try:
            result[name] = getter()
        except WunderTradingError as exc:
            errors[name] = str(exc)
    result["status"] = "OK" if not errors else "DEGRADED"
    result["errors"] = errors
    return result
