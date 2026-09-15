"""Evidence accumulation layer that runs beside paper learning without gating it.

The evidence machine is observational: it records causal shadow decisions, model
predictions, outcomes, and trade excursions. It never stops or approves the
paper-learning loop and never places live orders.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional

from src.agent_decision_layer import run_agent_council
from src.agent_evidence_attribution import AgentEvidenceAttribution


@dataclass
class Prediction:
    asset: str
    timestamp: str
    probability_up: float
    model_version: str
    outcome: Optional[int] = None


class EvidenceMachine:
    """Causal shadow-analysis and evidence collector.

    Paper execution is deliberately independent. Missing Q3/Q6/Q7 evidence is
    recorded as missing evidence, not converted into a veto of paper learning.
    """

    def __init__(self, max_bars: int = 500):
        self.max_bars = max_bars
        self.bars: Dict[str, List[dict]] = {}
        self.shadow: Dict[str, dict] = {}
        self.predictions: List[Prediction] = []
        self.events: List[dict] = []
        self.attribution = AgentEvidenceAttribution()

    @staticmethod
    def _probability_from_payload(payload: dict) -> Optional[float]:
        p = payload.get("ml_probability")
        if p is None:
            return None
        p = float(p)
        if not 0.0 <= p <= 1.0:
            raise ValueError("ml_probability must be in [0,1]")
        return p

    def observe(self, *, asset: str, price: float, timestamp: Optional[str] = None,
                bid: Optional[float] = None, ask: Optional[float] = None,
                volume: Optional[float] = None, payload: Optional[dict] = None) -> dict:
        payload = payload or {}
        ts = timestamp or datetime.now(timezone.utc).isoformat()
        row = {"timestamp": ts, "open": float(price), "high": float(price),
               "low": float(price), "close": float(price),
               "volume": float(volume or 0.0)}
        self.bars.setdefault(asset, []).append(row)
        self.bars[asset] = self.bars[asset][-self.max_bars:]

        ctx = {"bars": self.bars[asset], "data_quality_ok": True}
        if bid is not None and ask is not None:
            ctx.update({"bid": bid, "ask": ask})
        for key in ("buy_volume", "sell_volume", "macro_verified", "news_verified",
                    "macro_bias", "macro_confidence", "macro_risk", "dxy", "yields",
                    "model_version", "ml_probability", "ml_calibrated", "dataset_fingerprint"):
            if key in payload:
                ctx[key] = payload[key]
        council = run_agent_council(ctx)
        self.shadow[asset] = {"timestamp": ts, **council}
        self.events.append({"type": "shadow_council", "asset": asset, "timestamp": ts,
                            "decision": council["quantum_decision"],
                            "evidence_count": council["evidence_count"],
                            "hard_veto": council["hard_veto"]})
        self.attribution.record_council(
            asset=asset,
            timeframe=str(payload.get("timeframe", "UNKNOWN")),
            timestamp=ts,
            council=council,
        )

        p = self._probability_from_payload(payload)
        if p is not None and payload.get("model_version") and payload.get("ml_calibrated"):
            self.predictions.append(Prediction(asset, ts, p, str(payload["model_version"])))

        self._settle_predictions(asset, float(price))
        return council

    def _settle_predictions(self, asset: str, current_price: float) -> None:
        rows = self.bars.get(asset, [])
        if len(rows) < 2:
            return
        prev = float(rows[-2]["close"])
        if current_price == prev:
            return
        outcome = 1 if current_price > prev else 0
        for pred in self.predictions:
            if pred.asset == asset and pred.outcome is None and pred.timestamp != rows[-1]["timestamp"]:
                pred.outcome = outcome

    def brier(self, since: Optional[str] = None) -> Optional[float]:
        vals = []
        for p in self.predictions:
            if p.outcome is None:
                continue
            if since is not None and p.timestamp < since:
                continue
            vals.append((p.probability_up - p.outcome) ** 2)
        return sum(vals) / len(vals) if vals else None

    def latest_regime(self, asset: Optional[str] = None) -> str:
        row = self.shadow.get(asset) if asset else (next(reversed(self.shadow.values())) if self.shadow else None)
        return str((row or {}).get("agents", [{}])[0].get("evidence", {}).get("regime", "UNKNOWN"))

    def snapshot(self, asset: Optional[str] = None) -> dict:
        row = self.shadow.get(asset) if asset else (next(reversed(self.shadow.values())) if self.shadow else None)
        return {
            "research_only": True,
            "live_execution": False,
            "assets_observed": sorted(self.bars),
            "bars": {k: len(v) for k, v in self.bars.items()},
            "latest_regime": self.latest_regime(asset),
            "latest_shadow": row,
            "predictions": len(self.predictions),
            "settled_predictions": sum(p.outcome is not None for p in self.predictions),
            "brier": self.brier(),
            "events": len(self.events),
            "agent_attribution": {
                name: self.attribution.summary(name) for name in (f"Q{i}" for i in range(1, 9))
            },
        }
