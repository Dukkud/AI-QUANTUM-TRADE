# AI-QUANTUM v32

## Edge Validation & Agent Attribution

Version 32 is a research milestone. Its purpose is to measure whether added
research components improve out-of-sample trading quality after explicit costs.

### Scope

- Cost-aware R-multiple metrics.
- Feature attribution against a baseline.
- Sequential train/validation/OOS walk-forward windows.
- Calibration via Brier score.
- Fail-closed promotion gate.
- API boundary at `/research/edge-validation`.

### Feature groups

The intended comparison is:

1. `baseline`
2. `pine`
3. `midas`
4. `xau_research`
5. `all`

The implementation does not assume that any group is profitable. It only
measures the observations supplied by an upstream backtest or replay engine.

### Promotion rule

A candidate remains `HOLD` unless every supplied OOS window satisfies the
configured minimum trade count, positive expectancy, drawdown limit and
calibration limit. Empty OOS data never promotes.

### Execution boundary

v32 contains no broker order call and cannot enable live execution. The output
is research evidence only. A `PROMOTE` result means promotion to the next
research stage, not permission to trade real money.

### Required next evidence

- Real, versioned XAUUSD/BTCUSDT historical data.
- Native bid/ask or a defensible execution-cost model.
- Identical timestamps and causal feature construction across variants.
- Multiple walk-forward windows and regime slices.
- Forward paper trading after historical attribution.
