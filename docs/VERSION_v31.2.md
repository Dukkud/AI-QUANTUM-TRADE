# AI-QUANTUM v31.2

## Scope
v31.2 is the realtime market-data training layer. Agents operate in **TRAINING_ONLY / PAPER_ONLY** mode.

## Training universe
- Assets: XAUUSD, BTCUSDT
- Timeframes: 1M, 5M, 15M, 30M, 1H, 2H, 4H, 1D, 1W
- Agents: Q1-Q8

## Latency doctrine
Every training tick records exchange timestamp when supplied and local receive timestamp. Decision and simulated execution latency must be treated separately from market-data latency.

The agents must explicitly learn that paper execution is not equivalent to funded execution. Live execution can differ by milliseconds or more because of network delay, broker/exchange routing, queueing, spread, slippage, liquidity and infrastructure.

## Safety
v31.2 does not expose or enable live order placement. Binance API credentials are intentionally not required at this stage and must never be committed to source control.

## Versioning rule
From this point, incremental releases use the fixed sequence **v31.2, v31.3, v31.4, ...**. No reset to an earlier minor version for new functionality.
