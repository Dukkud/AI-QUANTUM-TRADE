from dataclasses import dataclass
from src.workgraph import NodeState

_ALLOWED={NodeState.READY:{NodeState.RUNNING,NodeState.FAILED},NodeState.RUNNING:{NodeState.WAITING,NodeState.VALIDATION,NodeState.COMPLETED,NodeState.FAILED},NodeState.WAITING:{NodeState.RUNNING,NodeState.FAILED},NodeState.VALIDATION:{NodeState.COMPLETED,NodeState.FAILED},NodeState.COMPLETED:set(),NodeState.FAILED:set()}

@dataclass
class WorkMachine:
    state: NodeState=NodeState.READY
    retries: int=0
    max_retries: int=2
    def transition(self,target:NodeState):
        if target not in _ALLOWED[self.state]: raise ValueError(f"invalid_transition:{self.state}->{target}")
        if target==NodeState.RUNNING and self.state==NodeState.WAITING: self.retries+=1
        self.state=target
    def recover(self):
        if self.state!=NodeState.FAILED: raise ValueError("not_failed")
        if self.retries < self.max_retries: self.state=NodeState.RUNNING
        else: raise RuntimeError("retry_budget_exhausted")
