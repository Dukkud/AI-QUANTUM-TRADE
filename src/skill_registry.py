from __future__ import annotations
from dataclasses import dataclass
from types import MappingProxyType

@dataclass(frozen=True)
class SkillManifest:
    skill_id: str
    version: str
    purpose: str
    allowed_agents: tuple[str, ...]
    allowed_actions: tuple[str, ...]
    risk_class: str
    max_latency_ms: int
    max_cost_units: float

    def __post_init__(self) -> None:
        if not self.skill_id or not self.version or not self.purpose:
            raise ValueError("identity required")
        if not self.allowed_agents:
            raise ValueError("allowed_agents required")
        if not self.allowed_actions:
            raise ValueError("allowed_actions required")
        if self.risk_class not in {"LOW", "MEDIUM", "HIGH"}:
            raise ValueError("invalid risk_class")
        if self.max_latency_ms <= 0 or self.max_cost_units < 0:
            raise ValueError("invalid budget")

class SkillRegistry:
    """Immutable runtime registry. Registration is declarative; execution is elsewhere."""
    def __init__(self, manifests: tuple[SkillManifest, ...] = ()) -> None:
        ids: set[str] = set()
        data: dict[str, SkillManifest] = {}
        for manifest in manifests:
            if manifest.skill_id in ids:
                raise ValueError("duplicate skill_id")
            ids.add(manifest.skill_id)
            data[manifest.skill_id] = manifest
        self._data = MappingProxyType(data)

    def get(self, skill_id: str) -> SkillManifest:
        return self._data[skill_id]

    def all(self) -> tuple[SkillManifest, ...]:
        return tuple(self._data.values())

    def authorize(self, skill_id: str, agent_id: str, action: str) -> bool:
        manifest = self.get(skill_id)
        return agent_id in manifest.allowed_agents and action in manifest.allowed_actions
