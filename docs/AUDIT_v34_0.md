# AI-QUANTUM-TRADE — Audit v34.0

## Scope
Shadow adaptive-weight proposal engine. This milestone does NOT enable adaptive production weights.

## Controls
- Proposal only; production weights are immutable.
- Requires both statistical evidence readiness and `STABLE` walk-forward status.
- Learning rate is bounded.
- Agent set must match exactly.
- Proposed weights are constrained by configurable floor/ceiling and sum to 1.
- HOLD is fail-closed whenever evidence or stability gates are not satisfied.
- `ADAPTIVE_WEIGHT_UPDATES=false` remains enforced in CI.

## Verification
Deterministic tests cover evidence/stability holds, bounded unit-sum proposals, input immutability, agent mismatch and infeasible bounds. GitHub Actions runs the v34.0 tests plus the complete prior evidence stack and safety invariants.

## Audit status
- Shadow proposal math: PASS by deterministic tests
- Fail-closed gates: PASS
- Production weight mutation: BLOCKED / absent
- ML training continuity: PRESERVED
- Live execution: BLOCKED
- GitHub current-head CI: PENDING until final workflow completion

## Important limitation
This is not a claim that adaptive weighting improves performance. A production weight change requires a separate controlled experiment, rollback mechanism, out-of-sample validation and governance approval.

## Post-v34.0 roadmap
1. v34.1 proposal ledger + versioned rollback snapshots.
2. v34.2 champion/challenger shadow experiment with locked OOS data.
3. v34.3 regime-conditioned calibration and stability monitoring.
4. v34.4 statistical sequential testing / multiple-comparison controls.
5. Only after those gates: controlled paper promotion; live execution remains separately gated.
