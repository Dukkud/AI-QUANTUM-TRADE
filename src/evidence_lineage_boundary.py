"""Fail-closed lineage boundary between predictions, evidence and learning."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class LineageInputs:
    prediction_id: str | None
    evidence_id: str | None
    outcome_id: str | None
    source_id: str | None
    dataset_id: str | None
    immutable_chain_valid: bool
    label_purge_valid: bool
    shadow_only: bool

@dataclass(frozen=True)
class LineageResult:
    status: str
    blockers: tuple[str, ...]

def validate_lineage(x: LineageInputs) -> LineageResult:
    blockers=[]
    for name,value in (("PREDICTION_ID",x.prediction_id),("EVIDENCE_ID",x.evidence_id),("SOURCE_ID",x.source_id),("DATASET_ID",x.dataset_id)):
        if not value: blockers.append(f"MISSING_{name}")
    if not x.immutable_chain_valid: blockers.append("EVIDENCE_CHAIN_INVALID")
    if not x.label_purge_valid: blockers.append("LABEL_PURGE_INVALID")
    if x.outcome_id is None and not x.shadow_only: blockers.append("OUTCOME_REQUIRED_FOR_NON_SHADOW")
    if not x.shadow_only: blockers.append("LEARNING_MUST_REMAIN_SHADOW")
    return LineageResult("PASS" if not blockers else "BLOCKED", tuple(blockers))
