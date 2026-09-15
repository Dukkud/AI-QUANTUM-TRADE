"""Skill -> evidence -> learning feedback, research-only and non-blocking."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Optional
import os
from src.evidence_persistence import JsonlEvidenceStore

@dataclass
class SkillEvidence:
    skill_name: str
    agent: str
    asset: str
    timeframe: str
    regime: str
    timestamp: str
    invoked: bool
    evidence_count: int = 0
    contribution: float = 0.0
    outcome_r: Optional[float] = None
    brier_delta: Optional[float] = None
    correct: Optional[bool] = None
    reliability: Optional[float] = None

class SkillEvidenceLedger:
    def __init__(self, path: Optional[str] = None):
        self.store = JsonlEvidenceStore(path or os.getenv("AI_QUANTUM_SKILL_EVIDENCE_PATH", "data/skill_evidence.jsonl"))
        self.records: list[SkillEvidence] = []
        self._load()

    def _load(self):
        for row in self.store.read_all():
            if row.get("type") == "skill_evidence":
                self.records.append(SkillEvidence(**{k: row.get(k) for k in SkillEvidence.__dataclass_fields__}))
            elif row.get("type") == "skill_settlement":
                for r in self.records:
                    if all(r.__dict__.get(k) == row.get(k) for k in ("skill_name", "agent", "asset", "timeframe", "timestamp")) and r.outcome_r is None:
                        r.outcome_r = float(row["outcome_r"]); r.brier_delta = row.get("brier_delta"); r.correct = row.get("correct"); r.reliability = row.get("reliability")

    def record(self, *, skill_name: str, agent: str, asset: str, timeframe: str, regime: str, timestamp: str, invoked: bool, evidence_count: int = 0, contribution: float = 0.0):
        row = SkillEvidence(skill_name, agent, asset, timeframe, regime, timestamp, invoked, int(evidence_count), float(contribution))
        self.records.append(row); self.store.append({"type":"skill_evidence", **asdict(row)}); return row

    def settle(self, *, skill_name: str, agent: str, asset: str, timeframe: str, timestamp: str, outcome_r: float, brier_delta: Optional[float] = None):
        changed = 0
        for r in self.records:
            if r.skill_name == skill_name and r.agent == agent and r.asset == asset and r.timeframe == timeframe and r.timestamp == timestamp and r.outcome_r is None:
                r.outcome_r=float(outcome_r); r.brier_delta=brier_delta
                r.correct = outcome_r > 0 if r.contribution > 0 else (outcome_r < 0 if r.contribution < 0 else None)
                rows=[x for x in self.records if x.skill_name==skill_name and x.agent==agent and x.outcome_r is not None]
                r.reliability=sum(1 for x in rows if x.correct)/len(rows) if rows else None
                self.store.append({"type":"skill_settlement", **{k:getattr(r,k) for k in ("skill_name","agent","asset","timeframe","timestamp")}, "outcome_r":r.outcome_r,"brier_delta":r.brier_delta,"correct":r.correct,"reliability":r.reliability}); changed += 1
        return changed

    def matrix(self):
        groups={}
        for r in self.records:
            key=(r.skill_name,r.agent,r.asset,r.timeframe,r.regime); g=groups.setdefault(key, {"observations":0,"settled":0,"mean_outcome_r":None,"accuracy":None,"mean_contribution":None})
            g["observations"]+=1
            if r.outcome_r is not None: g["settled"]+=1
        for key,g in groups.items():
            rows=[r for r in self.records if (r.skill_name,r.agent,r.asset,r.timeframe,r.regime)==key]; settled=[r for r in rows if r.correct is not None]
            g["mean_outcome_r"]=sum(r.outcome_r for r in rows if r.outcome_r is not None)/g["settled"] if g["settled"] else None
            g["accuracy"]=sum(1 for r in settled if r.correct)/len(settled) if settled else None
            g["mean_contribution"]=sum(r.contribution for r in rows)/len(rows)
        return {"research_only":True,"live_execution":False,"groups":[{"skill_name":k[0],"agent":k[1],"asset":k[2],"timeframe":k[3],"regime":k[4],**v} for k,v in groups.items()]}

    def integrity(self): return self.store.verify()
    def snapshot(self): return {"research_only":True,"live_execution":False,"records":len(self.records),"matrix":self.matrix(),"integrity":self.integrity()}
