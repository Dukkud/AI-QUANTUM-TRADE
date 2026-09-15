# AI-QUANTUM v34.1 — Skill → Evidence → Learning Feedback

## Purpose
v34.1 converts the curated skill registry from a static capability map into an observable research feedback layer. It records which skill is associated with which agent, asset, timeframe and regime, then settles the observation against paper outcomes.

## Learning continuity
The skill ledger is observational and non-blocking. Q1-Q8 paper execution, realtime learning and evidence collection continue even when a skill has insufficient evidence. Skill statistics are descriptive until minimum-sample, out-of-sample, calibration and anti-overfit gates permit their later use in agent weighting.

## Persistent evidence
`data/skill_evidence.jsonl` stores append-only skill observations and settlements. The ledger records:
- skill_name
- agent
- asset
- timeframe
- regime
- timestamp
- invoked
- evidence_count
- contribution
- outcome_r
- brier_delta
- correctness
- reliability

## Analytics
The matrix is grouped by `Skill × Agent × Asset × Timeframe × Regime` and exposes observations, settled outcomes, mean outcome R, accuracy and mean contribution.

## API
- `GET /evidence/skills`
- `GET /evidence/skills/matrix`
- `GET /evidence/skills/integrity`

## Safety
`research_only=true` and `live_execution=false`. This milestone does not enable broker/exchange orders and does not constitute evidence of trading profitability.

## Promotion rule
Skill reliability must not directly change production/live weights at v34.1. The next research milestone should add sample-size gates, OOS windows, regime stability, confidence intervals, leakage checks and explicit attribution deltas before skill evidence can influence Q-agent weights.
