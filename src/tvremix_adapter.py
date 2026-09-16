"""TVRemix MCP integration and data-validation boundary.

Research-only adapter. It never places orders and never mutates agent weights.
Secrets are read from TVREMIX_API_KEY and are never returned by API endpoints.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from collections import deque
import hashlib
import json
import os
import threading
import time
from typing import Any, Callable

import requests

DEFAULT_ENDPOINT = "https://tvremix.xyz/api/mcp/v1"
DEFAULT_PROTOCOL_VERSION = "2025-06-18"
SUPPORTED_TIMEFRAMES = ("1M", "5M", "15M", "30M", "1H", "2H", "4H", "1D", "1W")
DEFAULT_SYMBOLS = {"XAUUSD": "OANDA:XAUUSD", "BTCUSDT": "BINANCE:BTCUSDT"}


class TVRemixError(RuntimeError):
    pass


@dataclass(frozen=True)
class TVRemixConfig:
    endpoint: str = DEFAULT_ENDPOINT
    api_key_present: bool = False
    timeout_seconds: float = 20.0
    max_bars: int = 5000

    @classmethod
    def from_env(cls) -> "TVRemixConfig":
        return cls(
            endpoint=os.getenv("TVREMIX_MCP_URL", DEFAULT_ENDPOINT).rstrip("/"),
            api_key_present=bool(os.getenv("TVREMIX_API_KEY")),
            timeout_seconds=float(os.getenv("TVREMIX_TIMEOUT_SECONDS", "20")),
            max_bars=min(int(os.getenv("TVREMIX_MAX_BARS", "5000")), 5000),
        )


class _RateLimiter:
    def __init__(self) -> None:
        self._events = {"minute": deque(), "hour": deque(), "day": deque()}
        self._limits = {"minute": 20, "hour": 200, "day": 1500}
        self._lock = threading.Lock()

    def acquire(self) -> None:
        now = time.monotonic()
        windows = {"minute": 60.0, "hour": 3600.0, "day": 86400.0}
        with self._lock:
            for name, window in windows.items():
                q = self._events[name]
                while q and now - q[0] >= window:
                    q.popleft()
                if len(q) >= self._limits[name]:
                    raise TVRemixError(f"local rate limit reached: {name}")
            for q in self._events.values():
                q.append(now)


def _extract_json_from_response(response: Any) -> dict[str, Any]:
    content_type = str(response.headers.get("content-type", "")).lower()
    text = response.text or ""
    if "text/event-stream" in content_type or text.lstrip().startswith("event:") or text.lstrip().startswith("data:"):
        payloads: list[str] = []
        for line in text.splitlines():
            if line.startswith("data:"):
                value = line[5:].strip()
                if value and value != "[DONE]":
                    payloads.append(value)
        for raw in reversed(payloads):
            try:
                obj = json.loads(raw)
                if isinstance(obj, dict):
                    return obj
            except json.JSONDecodeError:
                continue
        raise TVRemixError("TVRemix returned an unreadable SSE response")
    try:
        obj = response.json()
    except Exception as exc:
        try:
            obj = json.loads(text)
        except Exception:
            raise TVRemixError("TVRemix returned non-JSON response") from exc
    if not isinstance(obj, dict):
        raise TVRemixError("TVRemix returned an invalid JSON-RPC object")
    return obj


def _find_ohlcv_rows(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        if value and all(isinstance(x, dict) for x in value[: min(len(value), 5)]):
            keys = {str(k).lower() for x in value[:5] for k in x.keys()}
            if {"open", "high", "low", "close"}.issubset(keys):
                return value
        for item in value:
            found = _find_ohlcv_rows(item)
            if found:
                return found
    elif isinstance(value, dict):
        for item in value.values():
            found = _find_ohlcv_rows(item)
            if found:
                return found
    return []


def _field(row: dict[str, Any], *names: str) -> Any:
    lowered = {str(k).lower(): v for k, v in row.items()}
    for name in names:
        if name.lower() in lowered:
            return lowered[name.lower()]
    return None


@dataclass(frozen=True)
class TVRemixValidation:
    valid: bool
    symbol: str
    timeframe: str
    rows: int
    duplicates: int
    non_monotonic: int
    gaps: int
    invalid_ohlc: int
    missing_timestamps: int
    source: str
    fingerprint: str
    errors: tuple[str, ...]
    warnings: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class TVRemixValidator:
    """Validate TVRemix OHLCV without treating vendor analysis as ground truth."""

    @staticmethod
    def validate(rows: list[dict[str, Any]], symbol: str, timeframe: str, *, source: str = "tvremix") -> TVRemixValidation:
        errors: list[str] = []
        warnings: list[str] = []
        normalized: list[dict[str, Any]] = []
        seen: set[float] = set()
        duplicates = 0
        non_monotonic = 0
        invalid_ohlc = 0
        missing_timestamps = 0
        timestamps: list[float] = []

        for idx, row in enumerate(rows):
            ts = _field(row, "timestamp", "time", "ts", "datetime", "date")
            o, h, l, c = (_field(row, x) for x in ("open", "high", "low", "close"))
            v = _field(row, "volume")
            if ts is None:
                missing_timestamps += 1
                continue
            try:
                ts_num = float(ts)
            except (TypeError, ValueError):
                missing_timestamps += 1
                continue
            if ts_num > 10_000_000_000:
                ts_num /= 1000.0
            timestamps.append(ts_num)
            if ts_num in seen:
                duplicates += 1
            seen.add(ts_num)
            try:
                vals = [float(o), float(h), float(l), float(c)]
                if not (vals[2] <= vals[0] <= vals[1] and vals[2] <= vals[3] <= vals[1]):
                    invalid_ohlc += 1
                if v is not None and float(v) < 0:
                    errors.append(f"negative volume at row {idx}")
                normalized.append({"timestamp": ts_num, "open": vals[0], "high": vals[1], "low": vals[2], "close": vals[3], "volume": None if v is None else float(v)})
            except (TypeError, ValueError):
                invalid_ohlc += 1

        for a, b in zip(timestamps, timestamps[1:]):
            if b <= a:
                non_monotonic += 1
        if invalid_ohlc:
            errors.append(f"invalid OHLC rows: {invalid_ohlc}")
        if duplicates:
            errors.append(f"duplicate timestamps: {duplicates}")
        if non_monotonic:
            errors.append(f"non-monotonic timestamps: {non_monotonic}")
        if missing_timestamps:
            errors.append(f"missing/invalid timestamps: {missing_timestamps}")

        gaps = 0
        positive_deltas = [b - a for a, b in zip(timestamps, timestamps[1:]) if b > a]
        if len(positive_deltas) >= 3:
            positive_deltas.sort()
            expected = positive_deltas[len(positive_deltas) // 2]
            if expected > 0:
                gaps = sum(1 for d in positive_deltas if d > expected * 1.5)
                if gaps:
                    warnings.append(f"detected {gaps} temporal gaps; no filling performed")

        fingerprint = hashlib.sha256(json.dumps(normalized, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        if not rows:
            warnings.append("no OHLCV rows returned")
        valid = not errors and bool(normalized)
        return TVRemixValidation(valid, symbol, timeframe, len(normalized), duplicates, non_monotonic, gaps, invalid_ohlc, missing_timestamps, source, fingerprint, tuple(errors), tuple(warnings))


class TVRemixClient:
    def __init__(self, config: TVRemixConfig | None = None, *, session: Any | None = None, transport: Callable[..., Any] | None = None) -> None:
        self.config = config or TVRemixConfig.from_env()
        self.session = session or requests.Session()
        self.transport = transport
        self._request_id = 0
        self._session_id: str | None = None
        self._initialized = False
        self._rate_limiter = _RateLimiter()

    @property
    def configured(self) -> bool:
        return bool(self.config.api_key_present)

    def _key(self) -> str:
        key = os.getenv("TVREMIX_API_KEY", "")
        if not key:
            raise TVRemixError("TVREMIX_API_KEY is not configured")
        return key

    def _post(self, payload: dict[str, Any], *, expect_response: bool = True) -> dict[str, Any]:
        self._rate_limiter.acquire()
        headers = {"Authorization": f"Bearer {self._key()}", "Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
        if self._session_id:
            headers["Mcp-Session-Id"] = self._session_id
        if self.transport:
            response = self.transport(self.config.endpoint, headers=headers, json=payload, timeout=self.config.timeout_seconds)
        else:
            response = self.session.post(self.config.endpoint, headers=headers, json=payload, timeout=self.config.timeout_seconds)
        if response.status_code == 429:
            raise TVRemixError(f"TVRemix rate limited; Retry-After={response.headers.get('Retry-After', 'unknown')}")
        if response.status_code >= 400:
            raise TVRemixError(f"TVRemix HTTP {response.status_code}")
        session_id = response.headers.get("Mcp-Session-Id")
        if session_id:
            self._session_id = session_id
        if not expect_response or response.status_code == 202:
            return {}
        obj = _extract_json_from_response(response)
        if "error" in obj:
            raise TVRemixError(f"TVRemix MCP error: {obj['error']}")
        return obj

    def initialize(self) -> dict[str, Any]:
        if self._initialized:
            return {"initialized": True, "session_id_present": bool(self._session_id)}
        self._request_id += 1
        result = self._post({"jsonrpc": "2.0", "id": self._request_id, "method": "initialize", "params": {"protocolVersion": DEFAULT_PROTOCOL_VERSION, "capabilities": {}, "clientInfo": {"name": "AI-QUANTUM-TRADE", "version": "34.2.0"}}})
        self._initialized = True
        self._post({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}, expect_response=False)
        return result.get("result", result)

    def tools_list(self) -> list[dict[str, Any]]:
        self.initialize()
        self._request_id += 1
        obj = self._post({"jsonrpc": "2.0", "id": self._request_id, "method": "tools/list", "params": {}})
        return list(obj.get("result", {}).get("tools", []))

    def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        self.initialize()
        self._request_id += 1
        obj = self._post({"jsonrpc": "2.0", "id": self._request_id, "method": "tools/call", "params": {"name": name, "arguments": arguments or {}}})
        return obj.get("result", obj)

    def find_tool(self, *names: str) -> dict[str, Any] | None:
        wanted = {n.lower() for n in names}
        return next((tool for tool in self.tools_list() if str(tool.get("name", "")).lower() in wanted), None)

    def get_ohlcv(self, symbol: str, timeframe: str, bars: int = 5000) -> dict[str, Any]:
        if timeframe not in SUPPORTED_TIMEFRAMES:
            raise ValueError(f"unsupported timeframe: {timeframe}")
        bars = max(1, min(int(bars), self.config.max_bars))
        if not self.find_tool("get_ohlcv"):
            raise TVRemixError("TVRemix get_ohlcv tool is unavailable")
        result = self.call_tool("get_ohlcv", {"symbol": symbol, "interval": timeframe, "limit": bars})
        rows = _find_ohlcv_rows(result)
        validation = TVRemixValidator.validate(rows, symbol, timeframe)
        try:
            from src.tvremix_evidence import TVRemixEvidenceLedger
            TVRemixEvidenceLedger().append({"symbol": symbol, "timeframe": timeframe, **validation.as_dict()})
        except Exception as exc:
            # Evidence persistence is non-blocking; source validation remains the hard result.
            if os.getenv("AI_QUANTUM_STRICT_EVIDENCE", "0") == "1":
                raise TVRemixError(f"TVRemix evidence persistence failed: {exc}") from exc
        return {"result": result, "rows": rows, "validation": validation.as_dict()}

    def status(self) -> dict[str, Any]:
        return {"configured": self.configured, "endpoint": self.config.endpoint, "research_only": True, "live_execution": False, "secret_exposed": False, "session_established": self._session_id is not None}
