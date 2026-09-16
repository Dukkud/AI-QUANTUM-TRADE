"""Operational SLO calculations for the evidence/learning plane."""
from __future__ import annotations
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class SLOResult:
    availability: float
    freshness: float
    evidence_completeness: float
    status: str

def evaluate_slo(availability: float, freshness: float, evidence_completeness: float, *, min_availability=.999, min_freshness=.995, min_evidence=.99) -> SLOResult:
    vals=(availability,freshness,evidence_completeness)
    if not all(isfinite(float(v)) and 0 <= float(v) <= 1 for v in vals): raise ValueError('invalid SLO metric')
    status='PASS' if availability>=min_availability and freshness>=min_freshness and evidence_completeness>=min_evidence else 'REVIEW'
    return SLOResult(float(availability),float(freshness),float(evidence_completeness),status)
