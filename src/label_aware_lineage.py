"""Prediction lineage and label-aware purge controls.

This module prevents temporal leakage when a prediction's label depends on a
future holding/outcome interval. It is evaluation-only and never changes
agent weights, decisions, or execution state.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable, Sequence


@dataclass(frozen=True)
class LabeledPrediction:
    prediction_id: str
    prediction_at_utc: str
    label_start_utc: str
    label_end_utc: str


@dataclass(frozen=True)
class PurgedSplit:
    train: tuple[LabeledPrediction, ...]
    validation: tuple[LabeledPrediction, ...]
    embargo: tuple[LabeledPrediction, ...]
    oos: tuple[LabeledPrediction, ...]


def _ts(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include timezone")
    return parsed


def validate_lineage(items: Iterable[LabeledPrediction]) -> None:
    seen: set[str] = set()
    for item in items:
        if not item.prediction_id or item.prediction_id in seen:
            raise ValueError("prediction_id must be unique")
        seen.add(item.prediction_id)
        prediction_at = _ts(item.prediction_at_utc)
        start = _ts(item.label_start_utc)
        end = _ts(item.label_end_utc)
        if start < prediction_at:
            raise ValueError("label_start_utc cannot precede prediction_at_utc")
        if end < start:
            raise ValueError("label_end_utc cannot precede label_start_utc")


def overlaps(a: LabeledPrediction, b: LabeledPrediction) -> bool:
    """Return True when two label intervals share any instant."""
    return _ts(a.label_start_utc) <= _ts(b.label_end_utc) and _ts(b.label_start_utc) <= _ts(a.label_end_utc)


def build_purged_split(
    observations: Sequence[LabeledPrediction],
    *,
    train_size: int,
    validation_size: int,
    oos_size: int,
    embargo: timedelta = timedelta(0),
) -> PurgedSplit:
    if min(train_size, validation_size, oos_size) <= 0 or embargo < timedelta(0):
        raise ValueError("invalid split sizes or embargo")
    items = sorted(observations, key=lambda x: _ts(x.prediction_at_utc))
    validate_lineage(items)
    if len(items) < train_size + validation_size + oos_size:
        raise ValueError("insufficient observations")
    train = tuple(items[:train_size])
    validation = tuple(items[train_size:train_size + validation_size])
    candidates = items[train_size + validation_size:]
    validation_label_end = max(_ts(x.label_end_utc) for x in validation)
    cutoff = validation_label_end + embargo
    embargo_items = tuple(x for x in candidates if _ts(x.prediction_at_utc) <= cutoff)
    oos_candidates = tuple(x for x in candidates if _ts(x.prediction_at_utc) > cutoff)
    # Purge OOS observations whose label interval overlaps any validation label.
    oos = tuple(x for x in oos_candidates if not any(overlaps(x, v) for v in validation))
    if len(oos) < oos_size:
        raise ValueError("insufficient leakage-safe OOS observations")
    return PurgedSplit(train, validation, embargo_items, oos[:oos_size])
