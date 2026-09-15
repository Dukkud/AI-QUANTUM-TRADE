# AI-QUANTUM-TRADE

Autonomous AI quantitative trading platform for XAUUSD and BTCUSDT with multi-agent analysis, risk management, adaptive learning and paper-to-live execution controls.

## v30 Autonomous Core

AI-QUANTUM uses eight analytical agents (Q1-Q8) coordinated by Quantum Core. The design follows the project specification: input validation, calculation, hypothesis, counter-hypothesis, probability, trade plan, confidence, veto, JSON output and feedback/reputation.

### Scope
- XAUUSD and BTCUSDT
- 1M / 5M / 15M / 30M / 1H / 2H / 4H / 1D / 1W
- Q1 Market State
- Q2 Structure & Liquidity
- Q3 Order Flow
- Q4 Quant
- Q5 Geometry & Cycles
- Q6 Macro / News / Geopolitics
- Q7 ML / Patterns
- Q8 Risk Gate

### Safety
The repository defaults to PAPER mode. Live execution is fail-closed and requires independent gates for real-data verification, data quality, source reconciliation, paper execution, risk validation, operator enablement and emergency-stop clearance. Adaptive logic cannot bypass these controls.

### Data boundaries
MT5 is the execution/data boundary for native broker ticks and bars. Kaggle is a historical-data acquisition boundary. Credentials are supplied through environment/secret storage and are never committed.

### Run locally
```bash
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```

Health endpoint: `/health`  
State endpoint: `/state`  
Decision endpoint: `/decision`

## Important
A passing software test suite does not establish trading profitability, live-data availability, broker execution readiness, or regulatory approval. Those require evidence from the target environment and controlled operational audits.

See `docs/DEPLOYMENT_PLAN_v30.md` for the staged roadmap.
