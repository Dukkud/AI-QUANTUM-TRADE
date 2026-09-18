# AI-QUANTUM-TRADE — v33.6 Audit

## Scope

v33.6 adds a rolling out-of-sample (OOS) evaluation layer over existing evidence. It separates chronological train, validation and OOS windows and supports segmentation by asset, timeframe, market regime and agent.

## Safety invariants

- The engine is observational and deterministic.
- It does not modify Q1–Q8 weights, retrain models, alter decisions, or place orders.
- `LIVE_TRADING=false`.
- `PAPER_EXECUTION=true`.
- `ADAPTIVE_WEIGHT_UPDATES=false`.
- Evidence remains outside the decision path.

## Implemented

- `src/rolling_oos.py`: validated timestamped observations, chronological rolling windows, segmentation and evaluation metrics.
- `tests/test_rolling_oos.py`: window construction, insufficient history, dimensional segmentation, metric determinism, immutability and fail-closed input validation.
- `.github/workflows/rolling-oos-validation.yml`: isolated CI gate with shadow-only environment invariants.

## Metrics

Accuracy, Brier score, mean realized R and maximum drawdown in R are calculated for OOS evidence. No metric is converted into a trading permission or weight update.

## Audit interpretation

PASS means the evaluation machinery is internally consistent. It does **not** mean an agent is profitable, statistically validated, or ready for live execution. Those conclusions require sufficiently large real-world evidence and leakage-resistant datasets.

## Known limitation

The current OOS engine consumes supplied evidence; it does not yet implement a persistent dataset registry, embargo/purge logic for overlapping labels, statistical confidence intervals, or automated model retraining. These are intentionally deferred to subsequent gates.

## Next gate: v33.7

Build the evidence dataset registry and leakage controls: immutable dataset manifests, source/version fingerprints, time-based purge/embargo, duplicate detection, train/validation/OOS lineage, and per-slice sample sufficiency. Continue ML training independently; do not enable adaptive weights or live execution from this milestone alone.
