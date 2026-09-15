# AI-QUANTUM v34 — Agent Skills Evidence Memory

## Objective
Add a provenance-aware skills layer to the evidence machine without stopping Q1-Q8 learning.

## Curated skills
- `web-research` → Q6/Q7: multi-source cited research.
- `explore-data` → Q3/Q4/Q7/Q8: dataset profiling, completeness, gaps, anomalies and temporal patterns.
- `cuml-machine-learning` → Q4/Q7: GPU ML for large tabular workloads when a compatible GPU runtime exists.
- `deep-agents-memory` → Q1-Q8: persistent/ephemeral/hybrid memory architecture. The production design keeps the existing append-only evidence ledgers as the audit source of truth.
- `code-review` → Q8: structured correctness/regression/test review.
- `writing-evals` → Q4/Q7/Q8: evaluation collections, scorers, offline/online/backtest evaluation concepts.
- `data-visualization` → Q4/Q8: evidence-bearing analytical visualization.
- `catalyst-calendar` → Q6/Q8: macro/market catalyst collection and outcome archiving.

## Source policy
The registry stores source repository, upstream URL and install command. Third-party full skill bodies are not copied into the repository; this avoids silently relicensing upstream material. The machine memory contains compact adapters/provenance and the upstream installation reference.

## Learning policy
Skills are capability instructions, not model-weight training data. They improve the agents' research/evaluation workflow and memory routing. Q1-Q8 paper learning continues independently.

## Safety
All registered skills are marked `research_only`. Skill installation or use cannot enable live execution. External skills that can write orders, sign transactions, or modify accounts are excluded from the v34 learning-memory set.

## Acceptance
1. Registry has unique skills.
2. Every Q1-Q8 agent has at least one mapped skill.
3. Persistent evidence machine exposes skill registry and validation state.
4. No live execution flag can be enabled through the skills registry.
5. CI must pass before the milestone is considered green.
