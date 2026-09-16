"""v34.4 cross-market gold triangulation, research-only.

Compares independent XAUUSD observations with Binance PAXG/XAUT observations.
No signal, order, or agent-weight mutation is performed here.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from math import sqrt
from statistics import mean
from typing import Any


@dataclass(frozen=True)
class TriangulationObservation:
    timestamp: str
    timeframe: str
    xauusd: float
    paxg: float
    xaut: float


class GoldTriangulationError(ValueError):
    pass


def _returns(values: list[float]) -> list[float]:
    if len(values) < 2:
        return []
    return [(b / a) - 1.0 for a, b in zip(values[:-1], values[1:]) if a > 0 and b > 0]


def _corr(a: list[float], b: list[float]) -> float | None:
    n = min(len(a), len(b))
    if n < 3:
        return None
    x, y = a[-n:], b[-n:]
    mx, my = mean(x), mean(y)
    dx, dy = [v - mx for v in x], [v - my for v in y]
    denom = sqrt(sum(v*v for v in dx) * sum(v*v for v in dy))
    return None if denom == 0 else sum(i*j for i, j in zip(dx, dy)) / denom


def _lead_lag(a: list[float], b: list[float], max_lag: int = 3) -> dict[str, float | None]:
    ra, rb = _returns(a), _returns(b)
    result: dict[str, float | None] = {}
    for lag in range(-max_lag, max_lag + 1):
        if lag > 0:
            x, y = ra[:-lag], rb[lag:]
        elif lag < 0:
            x, y = ra[-lag:], rb[:lag]
        else:
            x, y = ra, rb
        result[str(lag)] = _corr(x, y)
    return result


class GoldTriangulationEngine:
    """Descriptive relationship engine; it cannot change agent weights."""

    research_only = True
    live_execution = False

    def analyze(self, observations: list[TriangulationObservation]) -> dict[str, Any]:
        if len(observations) < 3:
            raise GoldTriangulationError("at least 3 synchronized observations are required")
        ordered = sorted(observations, key=lambda x: x.timestamp)
        if len({x.timestamp for x in ordered}) != len(ordered):
            raise GoldTriangulationError("duplicate timestamps are not allowed")
        xau = [x.xauusd for x in ordered]; paxg = [x.paxg for x in ordered]; xaut = [x.xaut for x in ordered]
        if any(v <= 0 for series in (xau, paxg, xaut) for v in series):
            raise GoldTriangulationError("prices must be positive")
        rx, rp, rt = _returns(xau), _returns(paxg), _returns(xaut)
        basis_paxg = [(p / x) - 1.0 for x, p in zip(xau, paxg)]
        basis_xaut = [(t / x) - 1.0 for x, t in zip(xau, xaut)]
        corrs = {
            "PAXG_XAUUSD": _corr(rx, rp),
            "XAUT_XAUUSD": _corr(rx, rt),
            "PAXG_XAUT": _corr(rp, rt),
        }
        lead_lag = {
            "PAXG_XAUUSD": _lead_lag(xau, paxg),
            "XAUT_XAUUSD": _lead_lag(xau, xaut),
            "PAXG_XAUT": _lead_lag(paxg, xaut),
        }
        max_pairs = max(corrs, key=lambda k: abs(corrs[k]) if corrs[k] is not None else -1.0)
        return {
            "research_only": True,
            "live_execution": False,
            "observations": len(ordered),
            "timestamp_start": ordered[0].timestamp,
            "timestamp_end": ordered[-1].timestamp,
            "basis": {
                "PAXG_XAUUSD_mean": mean(basis_paxg),
                "PAXG_XAUUSD_last": basis_paxg[-1],
                "XAUT_XAUUSD_mean": mean(basis_xaut),
                "XAUT_XAUUSD_last": basis_xaut[-1],
            },
            "correlation": corrs,
            "lead_lag": lead_lag,
            "strongest_pair_by_absolute_correlation": max_pairs,
            "weight_update": False,
            "decision": "EVIDENCE_ONLY",
        }


def observations_from_rows(rows: list[dict[str, Any]]) -> list[TriangulationObservation]:
    required = ("timestamp", "timeframe", "xauusd", "paxg", "xaut")
    out: list[TriangulationObservation] = []
    for row in rows:
        if any(k not in row for k in required):
            raise GoldTriangulationError("missing triangulation field")
        out.append(TriangulationObservation(str(row["timestamp"]), str(row["timeframe"]), float(row["xauusd"]), float(row["paxg"]), float(row["xaut"])))
    return out


def snapshot(observations: list[TriangulationObservation]) -> dict[str, Any]:
    result = GoldTriangulationEngine().analyze(observations)
    result["latest_observation"] = asdict(sorted(observations, key=lambda x: x.timestamp)[-1])
    return result
