# v34.5 XAUUSD Multi-Source

## Sources

- **Gold API**: keyless XAU spot via `https://api.gold-api.com/price/XAU`.
- **Yahoo Finance**: XAU/USD chart data via Yahoo symbol `XAUUSD=X`.

Gold API is used as an independent spot reference; Yahoo provides OHLC history/reference data. Gold API documents a free real-time price API with no authentication. Its terms also state that data are provided as-is and accuracy is not guaranteed, so it is a validation source rather than an execution authority.

## Safety contract

- research-only
- no order placement
- no automatic agent-weight mutation
- no live-gate enablement
- no synthetic fallback price
- invalid/empty/non-positive data fail closed

## Integration

`src/xau_multi_source.py` provides:

- `fetch_gold_api_quote()`
- `fetch_yahoo_xauusd(interval, bars)`
- `compare_spot(gold_quote, yahoo_last)`

The GitHub integration registry exposes both sources under `xauusd_market_data`.

The current application remains fail-closed and paper-only. External connectivity is not considered verified until a deployment smoke test successfully reaches both providers and records timestamps, symbol mapping, OHLC validity, gaps/duplicates and source latency.

## Evidence gate before using data for model promotion

1. Verify Gold API XAU spot and Yahoo XAUUSD=X concurrently.
2. Record receive timestamp and provider timestamp where available.
3. Compare spot basis and rolling return correlation.
4. Validate 9 target timeframes where the provider supports them.
5. Detect gaps, duplicates, clock misalignment and stale quotes.
6. Compare against an independent execution-grade XAUUSD feed.
7. Keep the source in evidence-only mode until OOS and forward-paper tests remain positive after costs.
