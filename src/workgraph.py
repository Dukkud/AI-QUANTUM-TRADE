from dataclasses import dataclass
from enum import Enum

class NodeState(str, Enum):
    READY="READY"; RUNNING="RUNNING"; WAITING="WAITING"; VALIDATION="VALIDATION"; COMPLETED="COMPLETED"; FAILED="FAILED"

@dataclass(frozen=True)
class WorkNode:
    node_id: str
    depends_on: tuple[str,...]=()
    state: NodeState=NodeState.READY

class Workgraph:
    def __init__(self, nodes: tuple[WorkNode,...]):
        ids={n.node_id for n in nodes}
        if len(ids)!=len(nodes): raise ValueError("duplicate_node")
        for n in nodes:
            if any(d not in ids for d in n.depends_on): raise ValueError("missing_dependency")
        self.nodes={n.node_id:n for n in nodes}
        self._assert_acyclic()
    def _assert_acyclic(self):
        visiting=set(); visited=set()
        def dfs(x):
            if x in visiting: raise ValueError("cycle")
            if x in visited: return
            visiting.add(x)
            for d in self.nodes[x].depends_on: dfs(d)
            visiting.remove(x); visited.add(x)
        for x in self.nodes: dfs(x)
    def ready(self)->tuple[str,...]:
        return tuple(n.node_id for n in self.nodes.values() if n.state==NodeState.READY and all(self.nodes[d].state==NodeState.COMPLETED for d in n.depends_on))
