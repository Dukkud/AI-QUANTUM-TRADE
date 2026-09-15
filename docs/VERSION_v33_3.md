# v33.3 — Agent Evidence Attribution

## Objective
Build a per-agent evidence trail without interrupting paper learning or realtime training.

## Contract
For every observed council event, Q1-Q8 receive an attribution record containing:
- timestamp, asset, timeframe;
- decision and confidence;
- evidence count and veto state;
- normalized contribution share;
- later outcome when available;
- optional MAE/MFE in R units.

Missing evidence remains `DATA_UNAVAILABLE`; it is not converted into a synthetic positive result.

## Safety
`research_only=true` and `live_execution=false`. This layer cannot enable live trading and is observational beside the learning loop.

## Interpretation
Attribution is evidence about contribution, not proof of causality or profitability. A larger contribution share is not automatically a better agent. Performance must be evaluated across multiple out-of-sample windows and regimes.
