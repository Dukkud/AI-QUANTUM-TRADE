"""AQ-RESEARCH: proprietary financial-intelligence ingestion and validation primitives.
No external scraping runtime is required. Network/browser adapters are injected at the edge.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from typing import Mapping, Protocol, Iterable

@dataclass(frozen=True)
class SourceDocument:
    source_id: str
    uri: str
    published_at: str
    retrieved_at: str
    content: str
    source_type: str = "WEB"

@dataclass(frozen=True)
class FinancialFact:
    entity: str
    metric: str
    value: object
    currency: str | None
    period: str | None
    source_id: str
    source_timestamp: str
    extraction_method: str
    evidence_span: str
    confidence: float
    verification_status: str
    version: int = 1
    information_time: str | None = None
    effective_from: str | None = None
    effective_to: str | None = None

@dataclass(frozen=True)
class ResearchEvent:
    event_id: str
    entity: str
    event_type: str
    effective_at: str
    source_id: str
    confidence: float

class DocumentFetcher(Protocol):
    def fetch(self, uri: str) -> SourceDocument: ...

class AQResearch:
    """Deterministic core; I/O is injected so tests never require live web access."""
    def __init__(self, fetcher: DocumentFetcher):
        self.fetcher = fetcher
        self._versions: dict[tuple[str,str], int] = {}

    @staticmethod
    def content_hash(document: SourceDocument) -> str:
        return sha256(document.content.encode("utf-8")).hexdigest()

    def validate_source(self, document: SourceDocument) -> bool:
        return bool(document.source_id and document.uri and document.content and document.published_at and document.retrieved_at)

    def extract_fact(self, document: SourceDocument, *, entity: str, metric: str, value: object,
                     currency: str | None, period: str | None, evidence_span: str,
                     confidence: float, information_time: str | None = None,
                     effective_from: str | None = None, effective_to: str | None = None) -> FinancialFact:
        if not self.validate_source(document):
            raise ValueError("invalid_source")
        if not (0.0 <= confidence <= 1.0):
            raise ValueError("invalid_confidence")
        if evidence_span not in document.content:
            raise ValueError("evidence_span_not_found")
        key=(entity,metric)
        version=self._versions.get(key,0)+1
        self._versions[key]=version
        status="verified" if confidence >= 0.90 else "review"
        return FinancialFact(entity,metric,value,currency,period,document.source_id,document.published_at,"AQ_NATIVE_EXTRACTION",evidence_span,confidence,status,version,information_time,effective_from,effective_to)

    @staticmethod
    def deduplicate(facts: Iterable[FinancialFact]) -> tuple[FinancialFact,...]:
        seen=set(); out=[]
        for f in facts:
            k=(f.entity,f.metric,f.value,f.period,f.source_id)
            if k not in seen:
                seen.add(k); out.append(f)
        return tuple(out)

    @staticmethod
    def resolve_entity(raw: str, aliases: Mapping[str,str]) -> str:
        return aliases.get(raw.strip(), raw.strip()).upper()

    @staticmethod
    def temporal_valid(fact: FinancialFact, as_of: str) -> bool:
        if fact.information_time and fact.information_time > as_of: return False
        if fact.effective_from and as_of < fact.effective_from: return False
        if fact.effective_to and as_of > fact.effective_to: return False
        return True

    @staticmethod
    def fact_to_evidence(fact: FinancialFact) -> dict:
        return {"entity":fact.entity,"metric":fact.metric,"value":fact.value,"currency":fact.currency,
            "period":fact.period,"source_id":fact.source_id,"source_timestamp":fact.source_timestamp,
            "extraction_method":fact.extraction_method,"evidence_span":fact.evidence_span,
            "confidence":fact.confidence,"verification_status":fact.verification_status,"version":fact.version,
            "information_time":fact.information_time,"effective_from":fact.effective_from,"effective_to":fact.effective_to}
