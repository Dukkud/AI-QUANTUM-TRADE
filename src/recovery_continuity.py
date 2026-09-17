"""Continuity and recovery gate for the evidence/learning plane."""
from __future__ import annotations
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class RecoveryResult:
    status: str
    blockers: tuple[str, ...]

def evaluate_recovery(*, backup_verified: bool, ledger_restorable: bool, replay_deterministic: bool, rto_minutes: float, rpo_minutes: float, max_rto=60.0, max_rpo=15.0) -> RecoveryResult:
    if not all(isfinite(float(x)) and x >= 0 for x in (rto_minutes, rpo_minutes, max_rto, max_rpo)):
        raise ValueError('invalid recovery targets')
    blockers=[]
    if not backup_verified: blockers.append('BACKUP_VERIFICATION')
    if not ledger_restorable: blockers.append('LEDGER_RESTORE')
    if not replay_deterministic: blockers.append('DETERMINISTIC_REPLAY')
    if rto_minutes > max_rto: blockers.append('RTO')
    if rpo_minutes > max_rpo: blockers.append('RPO')
    return RecoveryResult('PASS' if not blockers else 'REVIEW', tuple(blockers))
