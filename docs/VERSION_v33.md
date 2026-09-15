# AI-QUANTUM v33 — Proven Research Candidate

## Scope
v33 is the first milestone where Q1-Q8 have explicit analytical contracts rather than only labels inside the paper world. The layer is still research/paper-only.

## Q1-Q8 contract
| Agent | Required evidence | No evidence result |
|---|---|---|
| Q1 | causal OHLC history, regime features | INSUFFICIENT_DATA/HOLD |
| Q2 | causal highs/lows and structure | INSUFFICIENT_DATA/HOLD |
| Q3 | native bid/ask and buy/sell flow | DATA_UNAVAILABLE/HOLD |
| Q4 | >=30 realized R observations + probability + costs | INSUFFICIENT_DATA/HOLD |
| Q5 | causal range/geometry | INSUFFICIENT_DATA/HOLD |
| Q6 | verified macro/news feed | DATA_UNAVAILABLE/HOLD |
| Q7 | versioned calibrated model + dataset | DATA_UNAVAILABLE/HOLD |
| Q8 | data/risk/account/safety state | VETO on any hard failure |

## Decision semantics
`HOLD` is a decision only when evidence is sufficient and the calculated edge does not clear the gate. `N/A -> HOLD` is no longer represented as a valid trading decision: missing evidence is explicitly classified and propagated to Q8.

## v33 candidate gate
The candidate gate checks:
- net expectancy after commission, spread, slippage and latency assumptions;
- out-of-sample walk-forward windows;
- calibration via Brier score;
- regime robustness;
- per-agent attribution;
- anti-overfit/leakage checks.

Promotion can only be `PROMOTE_RESEARCH`. There is no `PROMOTE_LIVE` state in v33.

## Live safety
All new paths expose `research_only=true` and `live_execution=false`. Live trading remains behind the existing account verification, explicit client confirmation, safety gates and emergency-stop architecture.

## Data limitation
This release does **not** claim that a real external XAUUSD/BTCUSDT historical dataset has passed the full v33 evidence gate. The historical edge conclusion remains conditional until a versioned dataset with causal timestamps, defensible execution costs and independent review is supplied.
