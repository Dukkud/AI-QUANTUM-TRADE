# Final Audit v32

**Status: CONDITIONAL PASS / RESEARCH-ONLY**

## Implemented

- Pine v6 knowledge/validation layer remains isolated from execution.
- Midas multi-agent council remains research-only.
- XAU research features remain research-only.
- Cost-aware edge metrics are implemented in `src/edge_validation.py`.
- Feature attribution compares each research variant with a baseline under the same cost assumption.
- Walk-forward evaluation is sequential and does not shuffle observations.
- Brier score is reported for probability calibration.
- Promotion gate fails closed on empty/insufficient OOS evidence or failed thresholds.
- `/research/edge-validation` exposes the research calculations without changing live-gate state.

## Test evidence

The branch is intended to be validated by GitHub Actions for dependency install,
compileall, pytest and secret scan. Local execution can validate the dependency-
light edge module independently. Full-repository execution must be treated as
GitHub CI evidence when the execution sandbox cannot clone the private repo.

## Audit finding

v32 improves the scientific control layer, but it does **not** establish a
profitable trading edge by itself. Synthetic unit-test observations validate
mathematics and fail-closed behavior only. They are not market evidence.

## Release decision

Do not enable funded live trading based on v32. The appropriate next state is
historical replay -> walk-forward attribution -> cost stress -> regime analysis
-> forward paper trading -> independent review -> only then consideration of a
controlled live gate.

## Minimum promotion evidence

- positive net expectancy after realistic spread/commission/slippage;
- sufficient trade count in every required OOS window;
- no single window responsible for all performance;
- stable performance across relevant market regimes;
- acceptable calibration/Brier score;
- no lookahead or data leakage;
- native quote/execution evidence where available;
- paper-forward confirmation before any live activation.
