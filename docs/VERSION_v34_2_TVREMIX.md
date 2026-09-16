# v34.2 — TVRemix MCP Data Validation Layer

## Purpose

Integrate TVRemix as an external research market-data source without stopping Q1-Q8 paper learning and without introducing a live execution path.

## Source

- MCP endpoint: `https://tvremix.xyz/api/mcp/v1`
- Authentication: API key from environment variable `TVREMIX_API_KEY`
- API keys are never returned by application endpoints and must never be committed to GitHub.
- TVRemix documents MCP over Streamable HTTP and `Authorization: Bearer <key>` authentication.

## Boundary

`TVRemix -> adapter -> OHLCV validator -> provenance/fingerprint -> AI-QUANTUM evidence`

TVRemix output is treated as source evidence, not as ground truth. Vendor-provided BOS/CHoCH/OB/FVG/SMC conclusions are not automatically promoted to Q2 truth. OHLCV is not treated as native bid/ask order flow for Q3.

## Validation

The adapter validates:

- symbol and timeframe boundary;
- causal timestamp ordering;
- duplicate timestamps;
- missing timestamps;
- OHLC integrity (`Low <= Open/Close <= High`);
- negative volume;
- temporal gaps without silent filling;
- deterministic SHA-256 fingerprint of normalized rows;
- TVRemix MCP tool discovery before calling `get_ohlcv`.

Supported project timeframes: `1M, 5M, 15M, 30M, 1H, 2H, 4H, 1D, 1W`.

Default symbol mapping is configurable at the application boundary:

- XAUUSD -> `OANDA:XAUUSD`
- BTCUSDT -> `BINANCE:BTCUSDT`

The symbol mapping is a default, not an assertion that these are the only valid TradingView symbols.

## Safety

- `research_only=true`
- `live_execution=false`
- TVRemix cannot place broker orders through this adapter.
- Adapter errors fail closed for data use; they do not halt the learning loop.
- No adaptive weight is changed directly by TVRemix responses.

## API endpoints

- `GET /integrations/tvremix/status`
- `GET /integrations/tvremix/tools`
- `POST /integrations/tvremix/validate`
- `POST /integrations/tvremix/ohlcv`

The application reports configuration state, never the secret itself.

## Acceptance boundary

Software integration can pass before external source validation passes. A successful code test does not prove that the real TVRemix credential, real symbols, real-time freshness, or cross-source agreement have been validated in the deployment environment.

## Next evidence step

Run the adapter against real TVRemix for XAUUSD and BTCUSDT across all nine project timeframes, record source fingerprints and validation results, then compare the same timestamps against an independent source before marking TVRemix as a validated data source in the Evidence Machine.
