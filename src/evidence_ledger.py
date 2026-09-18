"""Tamper-evident local evidence ledger for AI-QUANTUM predictions.

The ledger is deliberately independent from the agent/ML decision path. It
stores immutable JSONL records and chains each record to the previous hash.
No secrets or credentials are accepted by this module.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

GENESIS = "0" * 64


@dataclass(frozen=True)
class PredictionEvidence:
    prediction_id: str
    observed_at_utc: str
    asset: str
    timeframe: str
    decision: str
    direction: str | None
    entry: float | None
    stop: float | None
    target: float | None
    probability: float | None
    agent_outputs: dict[str, Any]
    data_quality: float | None = None
    source: str = "ai-quantum"


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def record_hash(previous_hash: str, record: dict[str, Any]) -> str:
    payload = previous_hash + canonical_json(record)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class EvidenceLedger:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def _last_hash(self) -> str:
        if not self.path.exists() or self.path.stat().st_size == 0:
            return GENESIS
        last: dict[str, Any] | None = None
        with self.path.open("r", encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    last = json.loads(line)
        return str(last.get("record_hash", GENESIS)) if last else GENESIS

    def append(self, evidence: PredictionEvidence) -> str:
        if not evidence.prediction_id:
            raise ValueError("prediction_id is required")
        if not evidence.observed_at_utc:
            raise ValueError("observed_at_utc is required")
        record = asdict(evidence)
        record["recorded_at_utc"] = datetime.now(timezone.utc).isoformat()
        previous_hash = self._last_hash()
        digest = record_hash(previous_hash, record)
        envelope = {"previous_hash": previous_hash, "record_hash": digest, "record": record}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(canonical_json(envelope) + "\n")
        return digest

    def verify(self) -> tuple[bool, int, str]:
        previous = GENESIS
        count = 0
        if not self.path.exists():
            return True, 0, previous
        with self.path.open("r", encoding="utf-8") as fh:
            for line_number, line in enumerate(fh, 1):
                if not line.strip():
                    continue
                envelope = json.loads(line)
                if envelope.get("previous_hash") != previous:
                    return False, line_number, "previous_hash mismatch"
                expected = record_hash(previous, envelope["record"])
                if envelope.get("record_hash") != expected:
                    return False, line_number, "record_hash mismatch"
                previous = expected
                count += 1
        return True, count, previous
