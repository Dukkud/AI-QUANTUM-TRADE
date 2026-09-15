"""Curated Agent Skills memory/router for AI-QUANTUM.

This module stores provenance-aware skill metadata and maps skills to Q1-Q8.
It intentionally stores compact adapters, not copied third-party skill bodies.
Third-party instructions remain governed by their upstream repositories/licenses.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Iterable

@dataclass(frozen=True)
class SkillSpec:
    name: str
    source: str
    install: str
    purpose: str
    agents: tuple[str, ...]
    mode: str = "research_only"

SKILLS = (
    SkillSpec("web-research", "langchain-ai/deepagents", "npx skills add https://github.com/langchain-ai/deepagents --skill web-research", "multi-source cited research and subagent synthesis", ("Q6", "Q7")),
    SkillSpec("explore-data", "anthropics/knowledge-work-plugins", "npx skills add https://github.com/anthropics/knowledge-work-plugins --skill explore-data", "dataset profiling, quality, temporal gaps and anomaly discovery", ("Q3", "Q4", "Q7", "Q8")),
    SkillSpec("cuml-machine-learning", "langchain-ai/deepagents", "npx skills add https://github.com/langchain-ai/deepagents --skill cuml-machine-learning", "GPU ML for large tabular classification/regression/clustering workloads", ("Q4", "Q7")),
    SkillSpec("deep-agents-memory", "langchain-ai/langchain-skills", "npx skills add https://github.com/langchain-ai/langchain-skills --skill deep-agents-memory", "persistent, ephemeral and hybrid agent memory routing", ("Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8")),
    SkillSpec("code-review", "langchain-ai/deepagents", "npx skills add https://github.com/langchain-ai/deepagents --skill code-review", "structured correctness, regression and test review", ("Q8",)),
    SkillSpec("writing-evals", "axiomhq/writing-evals", "npx skills add https://github.com/axiomhq/writing-evals --skill writing-evals", "offline/online/backtest evaluation methodology and scorers", ("Q4", "Q7", "Q8")),
    SkillSpec("data-visualization", "langchain-ai/deepagents", "npx skills add https://github.com/langchain-ai/deepagents --skill data-visualization", "evidence-bearing charts and analytical summaries", ("Q4", "Q8")),
    SkillSpec("catalyst-calendar", "anthropics/financial-services", "npx skills add https://github.com/anthropics/financial-services --skill catalyst-calendar", "macro and market catalyst calendar with outcome archiving", ("Q6", "Q8")),
)


def registry() -> list[dict]:
    return [asdict(x) for x in SKILLS]


def skills_for_agent(agent: str) -> list[dict]:
    return [asdict(x) for x in SKILLS if agent in x.agents]


def validate_registry() -> dict:
    names = [x.name for x in SKILLS]
    return {
        "valid": len(names) == len(set(names)) and all(x.mode == "research_only" for x in SKILLS),
        "count": len(SKILLS),
        "agents": {f"Q{i}": len(skills_for_agent(f"Q{i}")) for i in range(1, 9)},
        "live_execution": False,
    }
