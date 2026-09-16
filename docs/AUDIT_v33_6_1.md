# AI-QUANTUM v33.6.1 Audit — Evidence Dataset Registry

## Scope
Adds deterministic dataset fingerprinting, duplicate-observation rejection and temporal embargo controls to the v33.6 rolling OOS evaluation branch.

## Safety invariants
- Evaluation only; no model-weight mutation.
- `LIVE_TRADING=false` remains required.
- `PAPER_EXECUTION=true` remains required.
- Evidence controls do not alter Q1-Q8 decision outputs.
- Duplicate or malformed temporal inputs fail closed.

## Local verification
Independent verification of the existing v33.6 metric fixture reproduced:
- Accuracy: 0.50
- Brier Score: 0.065 (floating representation: 0.06499999999999999)
- Mean Realized R: 0.25
- Max Drawdown R: 0.50

New deterministic tests cover:
1. stable dataset fingerprint independent of input ordering;
2. fingerprint change after content modification;
3. duplicate observation rejection;
4. validation/OOS embargo separation;
5. negative embargo rejection.

## GitHub status
The branch is under PR #19. GitHub Actions for Rolling OOS and Shadow Learning were observed running against the v33.6 head. Final PASS is withheld until the current head's complete workflow conclusions are green.

## Audit conclusion
Architecture: PASS.
Local mathematical verification: PASS.
Leakage-control implementation: PASS by deterministic tests.
GitHub runtime: PENDING until all current checks finish.
Production/live trading: BLOCKED by design.
Adaptive weight updates: BLOCKED by design.

## Next gate
v33.7 should expand this registry into immutable prediction/outcome lineage, dataset version manifests, purge rules for overlapping labels, and statistical confidence intervals. No adaptive weight changes should be enabled before sufficient real evidence and independent OOS validation exist.
