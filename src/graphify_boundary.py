from dataclasses import dataclass
from qgraph.adapter import QGraph, build_safe_inventory

@dataclass(frozen=True)
class GraphifyBoundary:
    upstream: str = "Graphify-Labs/graphify"
    release: str = "v8"
    package: str = "graphifyy"
    authority: str = "OBSERVE_EXPLAIN_PROPOSE"
    execution_enabled: bool = False

    def validate(self):
        if self.execution_enabled:
            raise ValueError("Graphify boundary cannot execute trades")
        if self.authority == "EXECUTE":
            raise ValueError("Graphify authority cannot be EXECUTE")
        return True

def build_qgraph_inventory(root: str):
    g = QGraph()
    for path in sorted(build_safe_inventory(root)):
        kind = "Document" if path.lower().endswith((".md", ".txt", ".pdf")) else "Version"
        g.add_node(kind, path, path)
    return g
