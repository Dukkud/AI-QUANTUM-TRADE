"""Objective 99%-readiness gate; never authorizes funded/live trading."""
from __future__ import annotations
from dataclasses import dataclass

CRITICAL_GATES = ('data','lineage','oos','risk','paper','security','recovery')
@dataclass(frozen=True)
class Readiness99:
    score: float
    status: str
    blockers: tuple[str, ...]

def evaluate_99(gates: dict[str, bool], *, threshold: float = 99.0) -> Readiness99:
    if not gates or not 0 < threshold <= 100: raise ValueError('invalid readiness input')
    blockers=tuple(sorted(k for k,v in gates.items() if not v))
    score=100.0*sum(bool(v) for v in gates.values())/len(gates)
    critical_missing=tuple(k for k in CRITICAL_GATES if not gates.get(k, False))
    status='READY_99_RESEARCH_PAPER' if score>=threshold and not critical_missing else 'BLOCKED'
    return Readiness99(score,status,tuple(sorted(set(blockers+critical_missing))))
