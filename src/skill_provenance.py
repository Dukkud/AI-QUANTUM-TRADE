from __future__ import annotations
from dataclasses import asdict, dataclass
import hashlib
import json

@dataclass(frozen=True)
class SkillInvocation:
    skill_id: str
    skill_version: str
    agent_id: str
    prediction_id: str
    asset: str
    timeframe: str
    regime: str
    input_hash: str
    source_ids: tuple[str, ...]
    tool_calls: tuple[str, ...]
    output_hash: str
    confidence: float
    latency_ms: int
    cost_units: float
    timestamp_utc: str
    policy_result: str

def canonical_hash(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def invocation_hash(invocation: SkillInvocation) -> str:
    return canonical_hash(asdict(invocation))
