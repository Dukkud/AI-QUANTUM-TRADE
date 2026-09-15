"""Per-agent evidence attribution layer.

Observational only: paper learning continues independently and live execution is
never enabled by this module. The layer records what each Q1-Q8 contributed,
then links that contribution to later outcomes for reproducible research.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional


AGENTS = [f"Q{i}" for i in range(1, 9)]


@dataclass
class AgentEvidence:
    agent: str
    timestamp: str
    asset: str
    timeframe: str
    decision: str
    confidence: float
    evidence_count: int
    veto: bool
    contribution: float
    outcome_r: Optional[float] = None
    correct: Optional[bool] = None
    mae_r: Optional[float] = None
    mfe_r: Optional[float] = None


class AgentEvidenceAttribution:
    """Append-oriented in-memory attribution ledger for the evidence pipeline."""

    def __init__(self) -> None:
        self.records: List[AgentEvidence] = []

    def record_council(self, *, asset: str, timeframe: str, timestamp: str,
                       council: dict, outcome_r: Optional[float] = None,
                       mae_r: Optional[float] = None, mfe_r: Optional[float] = None) -> List[dict]:
        agents = council.get("agents", [])
        by_name: Dict[str, dict] = {str(a.get("agent")): a for a in agents}
        total = sum(max(float(a.get("confidence", 0.0)), 0.0) for a in agents) or 1.0
        out: List[dict] = []
        for name in AGENTS:
            a = by_name.get(name, {})
            decision = str(a.get("decision", "DATA_UNAVAILABLE"))
            confidence = float(a.get("confidence", 0.0) or 0.0)
            contribution = confidence / total if confidence > 0 else 0.0
            veto = bool(a.get("veto", False))
            correct = None
            if outcome_r is not None and decision in {"LONG", "SHORT"}:
                correct = (outcome_r > 0) if decision == "LONG" else (outcome_r < 0)
            row = AgentEvidence(name, timestamp, asset, timeframe, decision,
                                confidence, int(a.get("evidence_count", 0) or 0),
                                veto, contribution, outcome_r, correct, mae_r, mfe_r)
            self.records.append(row)
            out.append(asdict(row))
        return out

    def summary(self, agent: Optional[str] = None) -> dict:
        rows = [r for r in self.records if agent is None or r.agent == agent]
        settled = [r for r in rows if r.correct is not None]
        wins = sum(1 for r in settled if r.correct)
        total_r = sum(float(r.outcome_r or 0.0) for r in settled)
        return {
            "research_only": True,
            "live_execution": False,
            "agent": agent or "ALL",
            "observations": len(rows),
            "settled": len(settled),
            "accuracy": wins / len(settled) if settled else None,
            "mean_outcome_r": total_r / len(settled) if settled else None,
            "mean_contribution": sum(r.contribution for r in rows) / len(rows) if rows else None,
            "veto_count": sum(1 for r in rows if r.veto),
        }
