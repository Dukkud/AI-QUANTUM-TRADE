"""Quantum Core: deterministic synthesis of Q1-Q9 outputs."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class AgentSignal:
    agent_id:str
    probability:float
    direction:str
    confidence:float

@dataclass(frozen=True)
class Consensus:
    probability:float
    direction:str
    agreement:float

def synthesize(signals:tuple[AgentSignal,...])->Consensus:
    if len(signals)!=9: raise ValueError("Q1_Q9_REQUIRED")
    if any(s.direction not in {"LONG","SHORT","FLAT"} for s in signals): raise ValueError("invalid_direction")
    longs=sum(s.direction=="LONG" for s in signals); shorts=sum(s.direction=="SHORT" for s in signals)
    direction="LONG" if longs>shorts else "SHORT" if shorts>longs else "FLAT"
    agreement=max(longs,shorts)/9
    return Consensus(sum(s.probability for s in signals)/9,direction,agreement)
