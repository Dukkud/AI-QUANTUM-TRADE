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
        if not proposal_id or not created_at_utc or not weights or any(float(v) < 0 for v in weights.values()):
            raise ValueError("invalid proposal record")
        if any(r.proposal_id == proposal_id for r in self._records):
            raise ValueError("duplicate proposal_id")
        parent = self._records[-1].proposal_id if self._records else None
        previous_hash = self._records[-1].sha256 if self._records else None
        payload = {"proposal_id": proposal_id, "parent_proposal_id": parent, "weights": {k: float(v) for k, v in sorted(weights.items())}, "created_at_utc": created_at_utc, "previous_hash": previous_hash}
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        record = ProposalRecord(proposal_id, parent, payload["weights"], created_at_utc, digest)
        self._records.append(record)
        return record

    def verify(self) -> bool:
        previous = None
        for index, record in enumerate(self._records):
            parent = self._records[index - 1].proposal_id if index else None
            payload = {"proposal_id": record.proposal_id, "parent_proposal_id": parent, "weights": record.weights, "created_at_utc": record.created_at_utc, "previous_hash": previous}
            expected = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            if expected != record.sha256 or record.parent_proposal_id != parent:
                return False
            previous = record.sha256
        return True

    def rollback_target(self, proposal_id: str) -> ProposalRecord:
        for record in self._records:
            if record.proposal_id == proposal_id:
                return record
        raise KeyError(proposal_id)
