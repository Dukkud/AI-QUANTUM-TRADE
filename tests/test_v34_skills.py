from src.skill_memory import registry, skills_for_agent, validate_registry


def test_skill_registry_is_research_only_and_unique():
    result = validate_registry()
    assert result["valid"] is True
    assert result["count"] == 8
    assert result["live_execution"] is False


def test_all_agents_have_memory_skills():
    for i in range(1, 9):
        assert skills_for_agent(f"Q{i}")


def test_critical_learning_skills_are_present():
    names = {x["name"] for x in registry()}
    assert {"deep-agents-memory", "explore-data", "cuml-machine-learning", "writing-evals"}.issubset(names)


def test_financial_research_skill_is_q6_scoped():
    row = next(x for x in registry() if x["name"] == "catalyst-calendar")
    assert row["role"] == ["Q6", "Q8"]
    assert row["install"].startswith("npx skills add")
