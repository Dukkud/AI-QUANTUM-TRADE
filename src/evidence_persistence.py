"""Append-only persistent evidence storage for research audit trails."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable, List


class JsonlEvidenceStore:
    """Small dependency-free append-only JSONL store with chained hashes."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.hash_path = self.path.with_suffix(self.path.suffix + ".sha256")

    @staticmethod
    def _canonical(row: dict) -> str:
        return json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    def append(self, row: dict) -> dict:
        payload = dict(row)
        payload.pop("chain_hash", None)
        previous = self.last_hash()
        payload["previous_hash"] = previous
        payload["chain_hash"] = hashlib.sha256((previous + self._canonical(payload)).encode("utf-8")).hexdigest()
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(self._canonical(payload) + "\n")
        self.hash_path.write_text(payload["chain_hash"] + "\n", encoding="utf-8")
        return payload

    def read_all(self) -> List[dict]:
        if not self.path.exists():
            return []
        rows: List[dict] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
        return rows

    def last_hash(self) -> str:
        rows = self.read_all()
        return str(rows[-1].get("chain_hash", "")) if rows else ""

    def verify(self) -> dict:
        rows = self.read_all()
        previous = ""
        for idx, row in enumerate(rows):
            expected = hashlib.sha256((previous + self._canonical({k: v for k, v in row.items() if k != "chain_hash"})).encode("utf-8")).hexdigest()
            if row.get("previous_hash", "") != previous or row.get("chain_hash") != expected:
                return {"valid": False, "records": len(rows), "failed_at": idx}
            previous = expected
        return {"valid": True, "records": len(rows), "last_hash": previous}
