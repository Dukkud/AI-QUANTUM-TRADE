"""Non-blocking evidence machine for causal research telemetry."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Dict, List, Optional
import os
from src.agent_decision_layer import run_agent_council
from src.agent_evidence_attribution import AgentEvidenceAttribution
from src.evidence_persistence import JsonlEvidenceStore
from src.skill_memory import registry as skill_registry, validate_registry

@dataclass
class Prediction:
    asset:str; timestamp:str; probability_up:float; model_version:str; outcome:Optional[int]=None

class EvidenceMachine:
    """Shadow evidence collection. It never gates paper learning or enables live orders."""
    def __init__(self,max_bars:int=500):
        self.max_bars=max_bars; self.bars:Dict[str,List[dict]]={}; self.shadow:Dict[str,dict]={}; self.predictions:List[Prediction]=[]; self.events=[]
        self.attribution=AgentEvidenceAttribution(); self.prediction_store=JsonlEvidenceStore(os.getenv('AI_QUANTUM_PREDICTION_PATH','data/predictions.jsonl')); self._load_predictions()

    def _load_predictions(self):
        for row in self.prediction_store.read_all():
            if row.get('type')=='prediction': self.predictions.append(Prediction(row['asset'],row['timestamp'],float(row['probability_up']),row['model_version'],row.get('outcome')))
        for row in self.prediction_store.read_all():
            if row.get('type')=='prediction_settlement':
                for p in self.predictions:
                    if p.asset==row['asset'] and p.timestamp==row['timestamp'] and p.outcome is None:p.outcome=row['outcome']

    @staticmethod
    def _probability_from_payload(payload):
        p=payload.get('ml_probability')
        if p is None:return None
        p=float(p)
        if not 0<=p<=1:raise ValueError('ml_probability must be in [0,1]')
        return p

    def observe(self,*,asset:str,price:float,timestamp:Optional[str]=None,bid:Optional[float]=None,ask:Optional[float]=None,volume:Optional[float]=None,payload:Optional[dict]=None)->dict:
        payload=payload or {}; ts=timestamp or datetime.now(timezone.utc).isoformat(); row={'timestamp':ts,'open':float(price),'high':float(price),'low':float(price),'close':float(price),'volume':float(volume or 0.0)}
        self.bars.setdefault(asset,[]).append(row); self.bars[asset]=self.bars[asset][-self.max_bars:]
        ctx={'bars':self.bars[asset],'data_quality_ok':True}
        if bid is not None and ask is not None:ctx.update({'bid':bid,'ask':ask})
        for key in ('buy_volume','sell_volume','macro_verified','news_verified','macro_bias','macro_confidence','macro_risk','dxy','yields','model_version','ml_probability','ml_calibrated','dataset_fingerprint'):
            if key in payload:ctx[key]=payload[key]
        council=run_agent_council(ctx); self.shadow[asset]={'timestamp':ts,**council}; self.events.append({'type':'shadow_council','asset':asset,'timestamp':ts,'decision':council['quantum_decision'],'evidence_count':council['evidence_count'],'hard_veto':council['hard_veto']})
        self.attribution.record_council(asset=asset,timeframe=str(payload.get('timeframe','UNKNOWN')),timestamp=ts,council=council)
        p=self._probability_from_payload(payload)
        if p is not None and payload.get('model_version') and payload.get('ml_calibrated'):
            pred=Prediction(asset,ts,p,str(payload['model_version'])); self.predictions.append(pred); self.prediction_store.append({'type':'prediction',**asdict(pred)})
        self._settle_predictions(asset,float(price)); return council

    def _settle_predictions(self,asset,current_price):
        rows=self.bars.get(asset,[])
        if len(rows)<2:return
        prev=float(rows[-2]['close'])
        if current_price==prev:return
        outcome=1 if current_price>prev else 0
        for pred in self.predictions:
            if pred.asset==asset and pred.outcome is None and pred.timestamp!=rows[-1]['timestamp']:
                pred.outcome=outcome; self.prediction_store.append({'type':'prediction_settlement','asset':asset,'timestamp':pred.timestamp,'outcome':outcome})

    def brier(self,since:Optional[str]=None):
        vals=[(p.probability_up-p.outcome)**2 for p in self.predictions if p.outcome is not None and (since is None or p.timestamp>=since)]
        return sum(vals)/len(vals) if vals else None

    def brier_history(self):
        out=[]
        for p in self.predictions:
            if p.outcome is not None:out.append({'asset':p.asset,'timestamp':p.timestamp,'model_version':p.model_version,'probability_up':p.probability_up,'outcome':p.outcome,'brier':(p.probability_up-p.outcome)**2})
        return out

    def latest_regime(self,asset=None):
        row=self.shadow.get(asset) if asset else (next(reversed(self.shadow.values())) if self.shadow else None)
        return str((row or {}).get('agents',[{}])[0].get('evidence',{}).get('regime','UNKNOWN'))

    def attribution_records(self): return self.attribution.records_as_dicts()
    def integrity(self): return {'attribution':self.attribution.integrity(),'predictions':self.prediction_store.verify()}

    def snapshot(self,asset=None):
        row=self.shadow.get(asset) if asset else (next(reversed(self.shadow.values())) if self.shadow else None)
        return {'research_only':True,'live_execution':False,'assets_observed':sorted(self.bars),'bars':{k:len(v) for k,v in self.bars.items()},'latest_regime':self.latest_regime(asset),'latest_shadow':row,'predictions':len(self.predictions),'settled_predictions':sum(p.outcome is not None for p in self.predictions),'brier':self.brier(),'brier_history':self.brier_history()[-500:],'events':len(self.events),'integrity':self.integrity(),'agent_attribution':{name:self.attribution.summary(name) for name in (f'Q{i}' for i in range(1,9))},'skill_memory':{'registry':skill_registry(),'validation':validate_registry()}}