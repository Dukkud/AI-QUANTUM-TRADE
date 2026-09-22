"""AQ-Orchestrator: trading-domain policy above AQ-Native Graph."""
from __future__ import annotations
from dataclasses import dataclass
from .agent_registry import ACTIVE_AGENTS

@dataclass(frozen=True)
class Task:
    task_id:str
    asset:str
    timeframe:str
    evidence_ids:tuple[str,...]

class AgentRegistry:
    def list(self): return ACTIVE_AGENTS
    def get(self,agent_id): return next(a for a in ACTIVE_AGENTS if a.agent_id==agent_id)

class AQOrchestrator:
    def __init__(self): self.registry=AgentRegistry()
    def plan(self,task:Task)->tuple[str,...]:
        if not task.evidence_ids: raise ValueError("evidence_required")
        return tuple(a.agent_id for a in self.registry.list())
    def route(self,agent_id:str)->str:
        self.registry.get(agent_id); return agent_id
