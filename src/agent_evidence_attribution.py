"""Per-agent evidence attribution layer with persistent research ledger."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
import os
from src.evidence_persistence import JsonlEvidenceStore
AGENTS=[f'Q{i}' for i in range(1,9)]; LONGISH={'LONG','BIAS_UP','TRADE'}; SHORTISH={'SHORT','BIAS_DOWN'}
@dataclass
class AgentEvidence:
    agent:str; timestamp:str; asset:str; timeframe:str; decision:str; confidence:float; evidence_count:int; veto:bool; contribution:float; outcome_r:Optional[float]=None; correct:Optional[bool]=None; mae_r:Optional[float]=None; mfe_r:Optional[float]=None
class AgentEvidenceAttribution:
    def __init__(self,path:Optional[str]=None): self.records:List[AgentEvidence]=[]; self.store=JsonlEvidenceStore(path or os.getenv('AI_QUANTUM_ATTRIBUTION_PATH','data/agent_attribution.jsonl')); self._load()
    def _load(self):
        rows=self.store.read_all()
        for row in rows:
            if row.get('type')=='agent_evidence': self.records.append(AgentEvidence(**{k:row.get(k) for k in AgentEvidence.__dataclass_fields__}))
        for row in rows:
            if row.get('type')=='agent_settlement':
                for r in self.records:
                    if r.agent==row.get('agent') and r.asset==row.get('asset') and r.timestamp==row.get('timestamp'): r.outcome_r=float(row['outcome_r']); r.mae_r=row.get('mae_r'); r.mfe_r=row.get('mfe_r'); r.correct=row.get('correct')
    def _persist(self,row): self.store.append({'type':'agent_evidence',**asdict(row)})
    def record_council(self,*,asset,timeframe,timestamp,council,outcome_r=None,mae_r=None,mfe_r=None):
        agents=council.get('agents',[]); by_name={str(a.get('agent')):a for a in agents}; total=sum(max(float(a.get('confidence',0.0)),0.0) for a in agents) or 1.0; out=[]
        for name in AGENTS:
            a=by_name.get(name,{}); decision=str(a.get('decision','DATA_UNAVAILABLE')); confidence=float(a.get('confidence',0.0) or 0.0); row=AgentEvidence(name,timestamp,asset,timeframe,decision,confidence,int(a.get('evidence_count',0) or 0),bool(a.get('veto',False)),confidence/total if confidence>0 else 0.0,outcome_r,self._correct(decision,outcome_r),mae_r,mfe_r); self.records.append(row); self._persist(row); out.append(asdict(row))
        return out
    @staticmethod
    def _correct(decision,outcome_r):
        if outcome_r is None or outcome_r==0:return None
        if decision in LONGISH:return outcome_r>0
        if decision in SHORTISH:return outcome_r<0
        return None
    def settle(self,*,asset,observation_timestamp,outcome_r,mae_r=None,mfe_r=None,agent:Optional[str]=None):
        changed=0
        for r in self.records:
            if r.asset==asset and r.timestamp==observation_timestamp and r.outcome_r is None and (agent is None or r.agent==agent):
                r.outcome_r=float(outcome_r); r.mae_r=mae_r; r.mfe_r=mfe_r; r.correct=self._correct(r.decision,r.outcome_r); changed+=1; self.store.append({'type':'agent_settlement','agent':r.agent,'asset':asset,'timestamp':observation_timestamp,'outcome_r':r.outcome_r,'mae_r':mae_r,'mfe_r':mfe_r,'correct':r.correct})
        return changed
    def summary(self,agent:Optional[str]=None):
        rows=[r for r in self.records if agent is None or r.agent==agent]; settled=[r for r in rows if r.correct is not None]; wins=sum(1 for r in settled if r.correct); total_r=sum(float(r.outcome_r or 0.0) for r in settled)
        return {'research_only':True,'live_execution':False,'agent':agent or 'ALL','observations':len(rows),'settled':len(settled),'accuracy':wins/len(settled) if settled else None,'mean_outcome_r':total_r/len(settled) if settled else None,'mean_contribution':sum(r.contribution for r in rows)/len(rows) if rows else None,'veto_count':sum(1 for r in rows if r.veto)}
    def records_as_dicts(self): return [asdict(r) for r in self.records]
    def integrity(self): return self.store.verify()
