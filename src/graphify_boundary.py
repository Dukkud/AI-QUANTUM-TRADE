from dataclasses import dataclass
from .qgraph.adapter import QGraph
@dataclass(frozen=True)
class GraphifyBoundary:
    upstream: str = "Graphify-Labs/graphify"
    release: str = "v8"
    package: str = "graphifyy"
    authority: str = "OBSERVE_EXPLAIN_PROPOSE"
    execution_enabled: bool = False
    def validate(self):
        if self.execution_enabled: raise ValueError("Graphify boundary cannot execute trades")
        if self.authority == "EXECUTE": raise ValueError("Graphify authority cannot be EXECUTE")
        return True

def build_qgraph_inventory(root: str):
    g=QGraph()
    for path in sorted(__import__('qgraph.adapter',fromlist=['build_safe_inventory']).build_safe_inventory(root)):
        g.add_node("Document" if path.lower().endswith(('.md','.txt','.pdf')) else "Version", path, path)
    return g
