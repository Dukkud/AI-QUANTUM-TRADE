# AI-QUANTUM v33.1 — CI + Persistent Hourly Telemetry

## Priority 1: CI
The CI workflow installs requirements, compiles `src` and `app.py`, runs pytest with `PYTHONPATH=.`, and performs a secret-pattern scan. v33.1 updates stale application-version assertions from the previous milestone.

## Priority 2: Persistent Hourly Telemetry Ledger
`src/hourly_telemetry.py` provides an append-only JSONL ledger. Default path is `data/hourly_telemetry.jsonl`, configurable with `AI_QUANTUM_TELEMETRY_PATH`.

Each hourly record stores:
- trades
- P&L
- win rate
- profit factor
- EV
- drawdown
- MAE/MFE
- Brier
- agent weights
- regime
- learning / experience
- loss debt
- quarantine
- errors
- gate state
- schema version

The application persists the paper-world hour on paper/realtime ticks and exposes `/telemetry/hourly` plus `/telemetry/hourly/close`. The hourly report also exposes a numeric Hour N vs Hour N-1 comparison.

## Semantics
A missing prior hour is explicitly reported as `NO_PREVIOUS_HOUR`. No metric is fabricated. Missing upstream evidence remains missing rather than being converted to a trading signal.

## Safety
Telemetry is observational and research/paper-only. It cannot enable live execution.
