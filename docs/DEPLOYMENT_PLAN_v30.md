# AI-QUANTUM v30 Autonomous Deployment Plan

## Objective
Build the audited v29.1 research/deployment candidate into a production-oriented autonomous trading platform for XAUUSD and BTCUSDT.

## Safety position
- Default mode: PAPER.
- Live execution is fail-closed.
- No credentials are stored in Git.
- No model may bypass Q8 Risk Gate.
- Live activation requires independent real-data verification, reconciliation, paper execution evidence, risk-engine validation, operator enablement, and emergency-stop clearance.

## Architecture
Data Layer -> Q1-Q7 -> Adversarial/Contradiction Check -> Quantum Core -> Q8 Risk Gate -> Paper/Controlled Execution -> Journal -> Calibration -> Adaptive Engine.

## Markets and timeframes
XAUUSD and BTCUSDT across 1M, 5M, 15M, 30M, 1H, 2H, 4H, 1D and 1W.

## Adaptive behavior
Agent weights are updated from calibrated performance, EV, robustness, regime score, independence and drawdown penalty. Agents can be quarantined when data quality or performance controls fail. The adaptive engine may reduce confidence, size, or trade frequency, but cannot disable safety gates.

## Delivery phases
1. Baseline audited v29.1 import.
2. Core contracts and deterministic engine.
3. Native MT5 tick/bar gateway.
4. Kaggle historical native-tick gateway.
5. Q1-Q8 agent contracts.
6. Quantum aggregation and calibration.
7. Paper execution and journal.
8. Walk-forward and cost-aware validation.
9. CI and audit reports.
10. Controlled-live readiness review.

A successful software build is not equivalent to profitable trading or regulatory approval. Those conclusions require evidence from real provider data and controlled operational testing.
