"""AQ-EVIDENCE BUS: one normalized, provenance-aware interface for intelligence inputs."""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json

@dataclass(frozen=True)
class EvidenceRecord:
    evidence_id: str
    source_id: str
    kind: str
    payload: dict
    information_time: str
    publication_time: str | None
    ingestion_time: str
    market_time: str | None
    effective_period: str | None
    confidence: float
    provenance_hash: str

class EvidenceBus:
    def __init__(self): self._records: dict[str,EvidenceRecord]={}
    def publish(self, *, source_id:str, kind:str, payload:dict, information_time:str, ingestion_time:str,
                publication_time:str|None=None, market_time:str|None=None, effective_period:str|None=None,
                confidence:float=1.0)->EvidenceRecord:
        raw=json.dumps(payload,sort_keys=True,separators=(",",":"))
        eid="ev_"+sha256((source_id+kind+raw+information_time).encode()).hexdigest()[:20]
        rec=EvidenceRecord(eid,source_id,kind,payload,information_time,publication_time,ingestion_time,market_time,effective_period,confidence,sha256(raw.encode()).hexdigest())
        self._records[eid]=rec; return rec
    def get(self,evidence_id:str)->EvidenceRecord: return self._records[evidence_id]
    def all(self)->tuple[EvidenceRecord,...]: return tuple(self._records.values())
    def usable_as_of(self,evidence_id:str, as_of:str)->bool:
        return self._records[evidence_id].information_time <= as_of
