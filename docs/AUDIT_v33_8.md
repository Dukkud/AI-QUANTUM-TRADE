# AI-QUANTUM-TRADE — Audit v33.8

## Scope
Statistical evidence layer: Wilson confidence interval for accuracy, deterministic bootstrap confidence interval for mean realized R, and minimum-sample gate.

## Safety
The layer is descriptive/evaluation-only. It does not alter Q1-Q8 weights, decisions, execution, or live mode. ML training continues independently.

## Verification
Deterministic tests cover interval bounds, invalid inputs, reproducibility, insufficient evidence, sufficient evidence and data-shape mismatch. GitHub Actions repeats these tests plus the v33.7/v33.6 evidence stack and safety invariants.

## Audit status
- Statistical calculations: PASS by deterministic tests
- Reproducibility: PASS
- Minimum evidence gate: PASS
- Adaptive learning: BLOCKED
- Live execution: BLOCKED
- GitHub current-head CI: PENDING until completion on final commit

## Interpretation rule
`EVIDENCE_READY` means the configured minimum sample requirement is met. It is not a claim that an agent is profitable or superior. Confidence intervals describe uncertainty and must be interpreted with the sampling design and market regime in view.

## Next gate
v33.9: walk-forward stability and regime/timeframe robustness, using the lineage-safe OOS evidence and statistical gates. No automatic weight mutation.
