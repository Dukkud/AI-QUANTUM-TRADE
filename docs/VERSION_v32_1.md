# AI-QUANTUM-TRADE v32.1

## Milestone
**Audit Hardening / Evidence Gate**

v32.1 is a controlled continuation of v32 Edge Validation. It does not claim a profitable trading strategy and does not authorize funded/live execution.

## Added
- Fail-closed research evidence gate.
- Explicit evidence requirements for real/versioned historical data, realistic execution costs, causal timestamps, leakage controls, multiple OOS windows, regime robustness, calibration, positive net expectancy after costs, forward paper validation and independent review.
- API endpoint: `POST /research/evidence-gate`.
- Application version: `32.1.0`.
- Explicit `live_gate_enablement: false` in the evidence gate result.

## Promotion semantics
- `HOLD` = insufficient evidence; proceed with research only.
- `PROMOTE_RESEARCH` = evidence is sufficient for the next research stage only.
- No v32.1 state can enable live execution.

## Next boundary: v33
The next substantive milestone is Historical Replay & Real Market Attribution using versioned real XAUUSD/BTCUSDT data, native bid/ask where available or a defensible cost model, causal replay, multiple OOS windows, regime analysis, agent attribution, calibration, cost stress and forward paper validation.

A positive synthetic/unit-test result is not evidence of market profitability.
