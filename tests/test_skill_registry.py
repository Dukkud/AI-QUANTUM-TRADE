import pytest
from src.skill_registry import SkillManifest, SkillRegistry

def test_registry_is_immutable_and_authorizes():
    manifest = SkillManifest("web-research", "1.0.0", "read-only research", ("Q6",), ("READ",), "MEDIUM", 1500, 2.0)
    registry = SkillRegistry((manifest,))
    assert registry.authorize("web-research", "Q6", "READ")
    assert not registry.authorize("web-research", "Q1", "READ")
    with pytest.raises(TypeError):
        registry._data["x"] = manifest

def test_registry_rejects_duplicates_and_bad_budget():
    manifest = SkillManifest("x", "1", "p", ("Q1",), ("READ",), "LOW", 1, 0)
    with pytest.raises(ValueError):
        SkillRegistry((manifest, manifest))
    with pytest.raises(ValueError):
        SkillManifest("x", "1", "p", ("Q1",), ("READ",), "LOW", 0, 0)
