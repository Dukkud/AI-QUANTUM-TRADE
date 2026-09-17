from dataclasses import dataclass, asdict
from hashlib import sha256
import json
from pathlib import Path
from .schema import NODE_TYPES, EDGE_TYPES, TRUST_LEVELS
SECRET_NAMES = {".env", ".env.local", ".env.production", "id_rsa", "id_ed25519"}
SECRET_TOKENS = ("API_KEY", "SECRET", "TOKEN", "PRIVATE_KEY", "PASSWORD", "BROKER_CREDENTIAL")
@dataclass(frozen=True)
class GraphNode:
    node_id: str
    node_type: str
    label: str
    source: str
    trust: str = "EXTRACTED"
@dataclass(frozen=True)
class GraphEdge:
    source: str
    target: str
    edge_type: str
    trust: str = "EXTRACTED"
class QGraph:
    """Deterministic structural graph boundary. Never a trading decision engine."""
    def __init__(self): self.nodes = {}; self.edges = []
    @staticmethod
    def _id(node_type, label): return sha256(f"{node_type}:{label}".encode()).hexdigest()[:16]
    def add_node(self, node_type, label, source, trust="EXTRACTED"):
        if node_type not in NODE_TYPES: raise ValueError("invalid node type")
        if trust not in TRUST_LEVELS: raise ValueError("invalid trust level")
        node_id = self._id(node_type, label); self.nodes[node_id] = GraphNode(node_id,node_type,label,source,trust); return node_id
    def add_edge(self, source, target, edge_type, trust="EXTRACTED"):
        if source not in self.nodes or target not in self.nodes: raise KeyError("both edge endpoints must exist")
        if edge_type not in EDGE_TYPES or trust not in TRUST_LEVELS: raise ValueError("invalid graph edge")
        self.edges.append(GraphEdge(source,target,edge_type,trust))
    def to_dict(self): return {"nodes":[asdict(n) for n in self.nodes.values()],"edges":[asdict(e) for e in self.edges]}
    def write_json(self, path): Path(path).write_text(json.dumps(self.to_dict(),indent=2,sort_keys=True),encoding="utf-8")
def is_secret_path(path):
    p=Path(path)
    return p.name in SECRET_NAMES or any(t in p.name.upper() for t in SECRET_TOKENS)
def build_safe_inventory(root):
    root_path=Path(root); return [str(p.relative_to(root_path)) for p in root_path.rglob('*') if p.is_file() and not is_secret_path(str(p))]
