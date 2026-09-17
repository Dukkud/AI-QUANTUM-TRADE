# VER1.0 Consolidation Audit

## Scope
VER1.0 is a controlled integration checkpoint built on the latest validated v36.8 head. It adds Q-GRAPH/Graphify without replacing the trading core.

## Controls
- Q1-Q8 remains the analytical decision system.
- Evidence Ledger remains trading-evidence source of truth.
- Graphify is non-critical to execution.
- Graph relationships are not profitability evidence.
- Secrets are excluded from graph inventory.
- Graphify cannot mutate model weights, risk policy, evidence, promotion state or execution.
- LIVE_TRADING remains disabled.
- Historical versions are retained as provenance.

## Local verification
A standalone VER1.0 + Graphify boundary suite passed locally: 3/3 tests plus compileall.

## GitHub verification
GitHub Actions is intentionally reserved for this final checkpoint. Previous v36.8 head had successful AI-QUANTUM CI and v36.8 validation runs; the new VER1.0 checkpoint requires a fresh final control run.

## Limitation
GitHub Actions billing minutes are not exposed by the repository connector used here. The user reported a replenished 3,000-minute allowance. The project hard-stop remains: at <=100 remaining minutes, no next final checkpoint is uploaded without explicit user confirmation.
