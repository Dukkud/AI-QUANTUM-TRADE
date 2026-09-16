"""Rolling out-of-sample evaluation for shadow learning.

The engine creates deterministic train/validation/OOS windows from already
observed prediction outcomes. It is an evaluation layer only: it never trains,
changes weights, alters decisions, or enables live execution.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import isfinite
from typing import Iterable, Sequence


@dataclass(frozen=True)
class OOSObservation:
    timestamp_utc: str
    asset: str
    timeframe: str
    regime: str
    agent: str
    confidence: float
    correct: bool
    realized_r: float | None = None


@dataclass(frozen=True)
class RollingWindow:
    train: tuple[OOSObservation, ...]
    validation: tuple[OOSObservation, ...]
    oos: tuple[OOSObservation, ...]


@dataclass(frozen=True)
class OOSMetrics:
    samples: int
    accuracy: float
    brier_score: float
    mean_realized_r: float | None
    max_drawdown_r: float | None


def _ts(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("timestamp_utc must be ISO-8601") from exc
    if parsed.tzinfo is None:
        raise ValueError("timestamp_utc must include timezone")
    return parsed


def _validate(item: OOSObservation) -> None:
    _ts(item.timestamp_utc)
    if not item.asset or not item.timeframe or not item.regime or not item.agent:
        raise ValueError("asset, timeframe, regime and agent are required")
    if not isfinite(item.confidence) or not 0.0 <= item.confidence <= 1.0:
        raise ValueError("confidence must be finite and within [0, 1]")
    if item.realized_r is not None and not isfinite(item.realized_r):
        raise ValueError("realized_r must be finite")


def build_rolling_windows(
    observations: Iterable[OOSObservation],
    *,
    train_size: int = 60,
    validation_size: int = 20,
    oos_size: int = 20,
    step: int = 20,
) -> list[RollingWindow]:
    """Build chronological rolling windows after sorting by timestamp.

    Windows are global and deterministic; callers can segment by asset,
    timeframe, regime or agent before invoking this function.
    """
    if min(train_size, validation_size, oos_size, step) <= 0:
        raise ValueError("window sizes and step must be positive")
    items = list(observations)
    for item in items:
        _validate(item)
    items.sort(key=lambda x: _ts(x.timestamp_utc))

    total = train_size + validation_size + oos_size
    result: list[RollingWindow] = []
    start = 0
    while start + total <= len(items):
        result.append(
            RollingWindow(
                train=tuple(items[start : start + train_size]),
                validation=tuple(items[start + train_size : start + train_size + validation_size]),
                oos=tuple(items[start + train_size + validation_size : start + total]),
            )
        )
        start += step
    return result


def metrics(observations: Sequence[OOSObservation]) -> OOSMetrics:
    """Calculate evaluation metrics without mutating input observations."""
    if not observations:
        return OOSMetrics(0, 0.0, 0.0, None, 0.0)
    for item in observations:
        _validate(item)
    accuracy = sum(item.correct for item in observations) / len(observations)
    brier = sum((item.confidence - float(item.correct)) ** 2 for item in observations) / len(observations)
    realized = [item.realized_r for item in observations if item.realized_r is not None]
    mean_r = sum(realized) / len(realized) if realized else None
    peak = equity = max_dd = 0.0
    for r in realized:
        equity += r
        peak = max(peak, equity)
        max_dd = max(max_dd, peak - equity)
    return OOSMetrics(len(observations), accuracy, brier, mean_r, max_dd)


def segment(
    observations: Iterable[OOSObservation],
    *,
    asset: str | None = None,
    timeframe: str | None = None,
    regime: str | None = None,
    agent: str | None = None,
) -> list[OOSObservation]:
    """Filter evidence into an auditable asset/TF/regime/agent slice."""
    items = list(observations)
    for item in items:
        _validate(item)
    return [
        item for item in items
        if (asset is None or item.asset == asset)
        and (timeframe is None or item.timeframe == timeframe)
        and (regime is None or item.regime == regime)
        and (agent is None or item.agent == agent)
    ]
