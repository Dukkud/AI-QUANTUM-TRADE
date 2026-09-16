"""Evidence dataset registry and temporal leakage controls.

Evaluation-only layer. It fingerprints observations, rejects duplicate IDs,
and creates train/validation/OOS ranges with an embargo gap. It never changes
agent weights, decisions, or execution state.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib
import json
from typing import Iterable, Sequence


@dataclass(frozen=True)
class DatasetManifest:
    dataset_id: str
    observation_count: int
    first_timestamp_utc: str | None
    last_timestamp_utc: str | None
    sha256: str


@dataclass(frozen=True)
class LeakageWindow:
    train: tuple[object, ...]
    validation: tuple[object, ...]
    embargo: tuple[object, ...]
    oos: tuple[object, ...]


def _parse(ts: str) -> datetime:
    value = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    if value.tzinfo is None:
        raise ValueError("timestamp must include timezone")
    return value


def fingerprint(observations: Sequence[object]) -> str:
    rows = []
    for item in observations:
        ts = getattr(item, "timestamp_utc", None)
        if ts is None:
            raise ValueError("observation timestamp_utc is required")
        rows.append({k: getattr(item, k) for k in ("timestamp_utc", "asset", "timeframe", "regime", "agent", "confidence", "correct", "realized_r") if hasattr(item, k)})
    payload = json.dumps(rows, sort_keys=True, separators=(",", ":"), default=str).encode()
    return hashlib.sha256(payload).hexdigest()


def build_manifest(observations: Sequence[object], dataset_id: str) -> DatasetManifest:
    if not dataset_id:
        raise ValueError("dataset_id is required")
    ordered = sorted(observations, key=lambda x: _parse(x.timestamp_utc))
    return DatasetManifest(dataset_id, len(ordered), ordered[0].timestamp_utc if ordered else None, ordered[-1].timestamp_utc if ordered else None, fingerprint(ordered))


def reject_duplicate_observations(observations: Iterable[object]) -> None:
    seen: set[tuple[str, str, str, str, str]] = set()
    for item in observations:
        key = (item.timestamp_utc, item.asset, item.timeframe, item.regime, item.agent)
        if key in seen:
            raise ValueError("duplicate observation detected")
        seen.add(key)


def build_leakage_safe_windows(observations: Iterable[object], *, train_size: int, validation_size: int, embargo: timedelta, oos_size: int, step: int = 1) -> list[LeakageWindow]:
    if min(train_size, validation_size, oos_size, step) <= 0 or embargo < timedelta(0):
        raise ValueError("invalid window or embargo parameters")
    items = sorted(list(observations), key=lambda x: _parse(x.timestamp_utc))
    reject_duplicate_observations(items)
    total = train_size + validation_size + oos_size
    out: list[LeakageWindow] = []
    start = 0
    while start + train_size + validation_size <= len(items):
        tr = tuple(items[start:start + train_size])
        va = tuple(items[start + train_size:start + train_size + validation_size])
        cutoff = _parse(va[-1].timestamp_utc) + embargo
        eligible = [x for x in items[start + train_size + validation_size:] if _parse(x.timestamp_utc) >= cutoff]
        if len(eligible) < oos_size:
            break
        oo = tuple(eligible[:oos_size])
        out.append(LeakageWindow(tr, va, tuple(x for x in items[start + train_size + validation_size:] if _parse(x.timestamp_utc) < cutoff), oo))
        start += step
    return out
