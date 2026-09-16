# v34.3 — Binance Gold Token Research Block

## Scope
Add Binance Spot market-data analysis for **PAXGUSDT** and **XAUTUSDT** as a digital-gold layer alongside XAUUSD.

## UI contract
The precious-metals block exposes three separate buttons:
- XAUUSD
- PAXG
- XAUT

PAXG and XAUT are Binance market-data sources. XAUUSD must remain an independent reference source; the system must never fabricate XAUUSD from PAXG/XAUT.

## Data
Public Binance Spot endpoints are used for research market data. No Binance account key is required for the public klines/exchange-info path implemented here. Symbol availability is resolved dynamically from `exchangeInfo` before klines are accepted.

Supported timeframes: 1M, 5M, 15M, 30M, 1H, 2H, 4H, 1D, 1W.

Analysis fields: latest OHLCV, EMA20, EMA50, RSI14, ATR14 and a descriptive trend/regime hint.

## Evidence rules
- timestamps must be unique and monotonic;
- OHLC integrity is enforced;
- negative volume/trade counts are rejected;
- unsupported symbols/timeframes fail closed;
- Binance output is evidence, not ground truth;
- PAXG/XAUT are not treated as identical to spot gold;
- no synthetic Q3 order flow is inferred from OHLCV;
- all execution remains research/paper only.

## Learning continuity
This module is additive. It does not pause Q1-Q8, Paper World, Evidence Machine, attribution, telemetry or calibration. The next stage can use the PAXG/XAUT observations as additional features/evidence after out-of-sample and correlation validation.

## Next gate
Before allowing PAXG/XAUT evidence to change agent weights, validate:
1. real Binance connectivity in deployment;
2. symbol availability and provenance;
3. timestamp/gap integrity;
4. cross-source relationship to XAUUSD;
5. regime-dependent lead/lag and correlation;
6. incremental predictive value after costs;
7. no leakage and multiple OOS windows.

Live execution remains blocked.
