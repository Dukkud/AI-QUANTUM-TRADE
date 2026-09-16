# AI-QUANTUM v33.5 Audit — Calibration & Drift Shadow Gate

Date: 2026-09-17
Base milestone: v33.4 Shadow Learning Validation
Implementation branch: feat/v33-4-shadow-learning-validation

## Scope

v33.5 adds a deterministic calibration/drift comparison layer for Q1-Q8. It compares baseline and current agent evidence snapshots using explicit thresholds for accuracy deterioration, Brier-score deterioration, realized-R deterioration and confidence shift.

## Safety invariants

- LIVE_TRADING=false
- PAPER_EXECUTION=true
- ADAPTIVE_WEIGHT_UPDATES=false
- No order-placement method is introduced.
- No model weights are changed.
- No decision or risk gate is modified.
- The drift layer is observational and can run alongside ongoing ML training.

## Gate semantics

STABLE means no configured material drift was detected in a sufficiently sized sample. DRIFT_REVIEW means one or more configured deterioration thresholds were exceeded. INSUFFICIENT_EVIDENCE means the baseline or current sample is below the minimum threshold; no drift conclusion is permitted.

The default thresholds are explicit and versionable:

- minimum samples: 30 per compared snapshot
- maximum accuracy drop: 0.10
- maximum Brier increase: 0.05
- maximum mean realized-R drop: 0.50
- maximum absolute mean-confidence shift: 0.10

These are monitoring thresholds, not claims of statistical significance or profitability.

## Tests

Local isolated execution: PASS. The test set covers stable snapshots, insufficient evidence, simultaneous drift flags, exact threshold boundaries, agent mismatch rejection, invalid metrics, and custom thresholds.

Existing GitHub CI baseline: PASS on commit 7c988cdf6e2a8e8b979593550f08324bd49303d7, AI-QUANTUM CI run 348.

GitHub Actions execution for the new v33.5 commits must be observed before this milestone is marked CI-verified. Absence of a run is reported as PENDING rather than PASS.

## Audit findings

PASS — v33.5 is outside the decision path.
PASS — v33.5 does not mutate adaptive_engine state.
PASS — insufficient samples prevent a drift conclusion.
PASS — all four drift dimensions are deterministic and independently reported.
PASS — boundary values at configured limits are not treated as violations.
PASS — invalid or mismatched agent snapshots are rejected.
PASS — no new dependency is required.
PENDING — GitHub Actions runtime for the final v33.5 HEAD.
PENDING — secret-backed WunderTrading runtime ingestion.
PENDING — real linked prediction/outcome sample size.
PENDING — rolling out-of-sample validation.
PENDING — statistical significance testing and regime-conditioned drift.
BLOCKED — automatic adaptive weight changes until the above evidence gates are satisfied.

## Next technical gate

v33.6 should add rolling-window evaluation and regime/asset/timeframe segmentation without changing the decision path. Only after stable out-of-sample evidence is accumulated should a bounded, versioned, reversible weight-proposal layer be introduced. Proposed weights must first remain shadow-only and require evidence-integrity, calibration, drawdown and rollback gates.
