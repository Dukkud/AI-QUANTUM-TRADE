"""Tamper-evident ledger for shadow weight proposals and rollback snapshots."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Mapping


@dataclass(frozen=True)
class ProposalRecord:
    proposal_id: str
    parent_proposal_id: str | None
    weights: dict[str, float]
    created_at_utc: str
    sha256: str


class ProposalLedger:
    def __init__(self) -> None:
        self._records: list[ProposalRecord] = []

    @property
    def records(self) -> tuple[ProposalRecord, ...]:
        return tuple(self._records)

    def append(self, proposal_id: str, weights: Mapping[str, float], created_at_utc: str) -> ProposalRecord:
        if not proposal_id or not created_at_utc or any(float(v) < 0 for v in weights.values()):
            raise ValueError("invalid proposal record")
        if any(r.proposal_id == proposal_id for r in self._records):
            raise ValueError("duplicate proposal_id")
        payload = {
            "proposal_id": proposal_id,
            "parent_proposal_id": self._records[-1].proposal_id if self._records else None,
            "weights": {k: float(v) for k, v in sorted(weights.items())},
            "created_at_utc": created_at_utc,
            "previous_hash": self._records[-1].sha256 if self._records else None,
        }
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        record = ProposalRecord(payload["proposal_id"], payload["parent_proposal_id"], payload["weights"], created_at_utc, digest)
        self._records.append(record)
        return record

    def verify(self) -> bool:
        previous = None
        for r in self._records:
            payload = {"proposal_id": r.proposal_id, "parent_proposal_id": r.parent_proposal_id, "weights": r.weights, "created_at_utc": r.created_at_utc, "previous_hash": previous}
            expected = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            if expected != r.sha256 or r.parent_proposal_id != (self._records[self._records.index(r)-1].proposal_id if self._records.index(r) else None):
                return False
            previous = r.sha256
        return True

    def rollback_target(self, proposal_id: str) -> ProposalRecord:
        for r in self._records:
            if r.proposal_id == proposal_id:
                return r
        raise KeyError(proposal_id)
