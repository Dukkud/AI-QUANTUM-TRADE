"""Evidence analytics across agents, regimes, assets and timeframes.

This is descriptive research infrastructure. It does not rank agents, alter
weights, stop learning, or enable execution.
"""
from __future__ import annotations
from collections import defaultdict
from typing import Iterable, Optional

class EvidenceAnalytics:
    def __init__(self, records: Optional[Iterable[dict]] = None):
        self.records = list(records or [])

    def add(self, records: Iterable[dict]) -> None:
        self.records.extend(records)

    def grouped(self, *, by: str = "agent") -> dict:
        groups = defaultdict(list)
        for r in self.records:
            key = str(r.get(by, "UNKNOWN"))
            groups[key].append(r)
        out = {}
        for key, rows in sorted(groups.items()):
            settled = [r for r in rows if r.get("correct") is not None]
            wins = sum(bool(r.get("correct")) for r in settled)
            rs = [float(r["outcome_r"]) for r in settled if r.get("outcome_r") is not None]
            out[key] = {
                "observations": len(rows),
                "settled": len(settled),
                "accuracy": wins / len(settled) if settled else None,
                "mean_outcome_r": sum(rs) / len(rs) if rs else None,
                "mean_mae_r": self._mean(rows, "mae_r"),
                "mean_mfe_r": self._mean(rows, "mfe_r"),
                "mean_contribution": self._mean(rows, "contribution"),
            }
        return out

    @staticmethod
    def _mean(rows, key):
        vals = [float(r[key]) for r in rows if r.get(key) is not None]
        return sum(vals) / len(vals) if vals else None

    def matrix(self) -> dict:
        return {
            "by_agent": self.grouped(by="agent"),
            "by_asset": self.grouped(by="asset"),
            "by_timeframe": self.grouped(by="timeframe"),
            "by_regime": self.grouped(by="regime"),
            "research_only": True,
            "live_execution": False,
        }
