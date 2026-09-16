"""Append-only provenance ledger for TVRemix validation observations."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class TVRemixEvidence:
    observed_at: str
    symbol: str
    timeframe: str
    rows: int
    valid: bool
    duplicates: int
    non_monotonic: int
    gaps: int
    invalid_ohlc: int
    missing_timestamps: int
    fingerprint: str
    source: str = "tvremix"
    research_only: bool = True
    live_execution: bool = False

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class TVRemixEvidenceLedger:
    def __init__(self, path: str | None = None) -> None:
        self.path = Path(path or os.getenv("AI_QUANTUM_TVREMIX_EVIDENCE_PATH", "data/tvremix_evidence.jsonl"))
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, validation: dict[str, Any]) -> TVRemixEvidence:
        record = TVRemixEvidence(
            observed_at=datetime.now(timezone.utc).isoformat(),
            symbol=str(validation.get("symbol", "UNKNOWN")),
            timeframe=str(validation.get("timeframe", "UNKNOWN")),
            rows=int(validation.get("rows", 0)),
            valid=bool(validation.get("valid", False)),
            duplicates=int(validation.get("duplicates", 0)),
            non_monotonic=int(validation.get("non_monotonic", 0)),
            gaps=int(validation.get("gaps", 0)),
            invalid_ohlc=int(validation.get("invalid_ohlc", 0)),
            missing_timestamps=int(validation.get("missing_timestamps", 0)),
            fingerprint=str(validation.get("fingerprint", "")),
        )
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record.as_dict(), sort_keys=True) + "\n")
        return record

    def read_all(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        rows: list[dict[str, Any]] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
        return rows

    def integrity(self) -> dict[str, Any]:
        records = self.read_all()
        raw = json.dumps(records, sort_keys=True, separators=(",", ":"))
        return {
            "records": len(records),
            "fingerprint": hashlib.sha256(raw.encode()).hexdigest(),
            "research_only": True,
            "live_execution": False,
        }

    def snapshot(self) -> dict[str, Any]:
        records = self.read_all()
        return {
            "records": len(records),
            "latest": records[-1] if records else None,
            "path": str(self.path),
            "persistent": True,
            "research_only": True,
            "live_execution": False,
        }
