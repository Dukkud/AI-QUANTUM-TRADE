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

### XAUUSD data sources
- **Gold API (`XAU`)** is the canonical external spot-gold source for XAU/USD. Its current-price endpoint is public and requires no API key; the provider documents a 30-second cache recommendation. urlGold API documentationhttps://gold-api.com/docs
- **Yahoo Finance (`GC=F`)** is connected as an independent COMEX gold-futures reference. It is not silently treated as the same instrument as spot XAU/USD. Yahoo identifies `GC=F` as Gold futures on COMEX and provides OHLC/history. urlYahoo Finance GC=Fhttps://finance.yahoo.com/quote/GC%3DF/
- The reconciliation layer exposes both prices, timestamps and the futures-minus-spot basis. It never averages the two into a synthetic XAUUSD price.

Endpoint: `/data/xauusd`

### Safety
The repository defaults to PAPER mode. Live execution is fail-closed and requires independent gates for real-data verification, data quality, source reconciliation, paper execution, risk validation, operator enablement and emergency-stop clearance. Adaptive logic cannot bypass these controls.

### Data boundaries
MT5 is the execution/data boundary for native broker ticks and bars. Kaggle is a historical-data acquisition boundary. Gold API and Yahoo Finance are external research/reference boundaries for XAUUSD. Credentials are supplied through environment/secret storage and are never committed.

### Run locally
```bash
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```

Health endpoint: `/health`  
State endpoint: `/state`  
Decision endpoint: `/decision`  
XAUUSD source reconciliation: `/data/xauusd`

## Important
A passing software test suite does not establish trading profitability, live-data availability, broker execution readiness, or regulatory approval. Those require evidence from the target environment and controlled operational audits.

See `docs/DEPLOYMENT_PLAN_v30.md` for the staged roadmap.
