"""AQ-FEATURE FABRIC: turns validated evidence into versioned machine features."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Feature:
    feature_id:str
    name:str
    value:float
    evidence_id:str
    source_id:str
    information_time:str
    confidence:float
    version:int

class FeatureFabric:
    def __init__(self): self._versions:dict[str,int]={}
    def build(self, *, name:str, value:float, evidence_id:str, source_id:str, information_time:str, confidence:float)->Feature:
        v=self._versions.get(name,0)+1; self._versions[name]=v
        return Feature(f"feat:{name}:{v}",name,float(value),evidence_id,source_id,information_time,confidence,v)
    @staticmethod
    def no_lookahead(feature:Feature, as_of:str)->bool: return feature.information_time <= as_of
