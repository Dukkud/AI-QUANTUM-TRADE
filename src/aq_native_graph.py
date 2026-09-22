"""AQ-NATIVE-GRAPH: proprietary stateful graph execution primitives."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Any

@dataclass
class GraphState:
    values:dict[str,Any]=field(default_factory=dict)
    history:list[str]=field(default_factory=list)

@dataclass(frozen=True)
class Node:
    node_id:str
    fn:Callable[[GraphState],GraphState]

@dataclass(frozen=True)
class Edge:
    source:str
    target:str
    condition:Callable[[GraphState],bool]=lambda s: True

class AQNativeGraph:
    def __init__(self,nodes:tuple[Node,...],edges:tuple[Edge,...]):
        self.nodes={n.node_id:n for n in nodes}; self.edges=edges; self._validate()
    def _validate(self):
        if len(self.nodes)==0: raise ValueError("empty_graph")
        if any(e.source not in self.nodes or e.target not in self.nodes for e in self.edges): raise ValueError("missing_node")
        adj={k:[] for k in self.nodes}
        for e in self.edges: adj[e.source].append(e.target)
        visiting=set(); done=set()
        def dfs(x):
            if x in visiting: raise ValueError("cycle")
            if x in done:return
            visiting.add(x)
            for y in adj[x]:dfs(y)
            visiting.remove(x);done.add(x)
        for x in self.nodes:dfs(x)
    def run(self,state:GraphState,start:str)->GraphState:
        cur=start; visited=set()
        while True:
            if cur in visited: raise RuntimeError("runtime_cycle")
            visited.add(cur); state=self.nodes[cur].fn(state); state.history.append(cur)
            candidates=[e for e in self.edges if e.source==cur and e.condition(state)]
            if not candidates:return state
            cur=candidates[0].target

class CheckpointStore:
    def __init__(self): self._snapshots={}
    def save(self,key,state): self._snapshots[key]=GraphState(dict(state.values),list(state.history))
    def load(self,key): return self._snapshots[key]

class Replay:
    @staticmethod
    def same_history(a:GraphState,b:GraphState)->bool: return a.history==b.history
