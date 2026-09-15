# AI-QUANTUM v31 Final Audit

## Scope
Eight independent paper agents Q1-Q8 operate in an isolated virtual world. Each wallet starts at exactly USD 1,000. No real broker order is sent by the paper world.

## Capital rules
- Initial wallet: $1,000 USD/USDT.
- Visible wallet floor: $1,000.
- Position sizing is based on the current wallet balance.
- Profitable trades compound against the current balance, so repeated percentage returns compound geometrically rather than using a fixed $1,000 base.
- Losses accumulate in `loss_debt` while the visible wallet remains protected at the $1,000 floor.
- When accumulated loss debt reaches $1,000, the agent is quarantined for 5 days.
- During quarantine no new paper trade may be opened.
- At the end of the quarantine/review period, `unlock_after_review()` restores the wallet to $1,000 and clears loss debt; experience is increased to record the completed review cycle.

## Market-world outputs
The engine exposes market state, wallet balances, open positions, trade history, P&L, experience, and Entry/Stop-Loss/Target line objects through the application API.

## Live authorization
Live authorization requires: registered account, verified account, explicit client trading confirmation, real-data verification, data-quality pass, reconciliation pass, paper-execution pass, risk-engine pass, `LIVE_TRADING=true`, and emergency stop clear. The v31 paper world itself contains no live order call.

## Test status
GitHub Actions must pass compileall and the full pytest suite before merge. A previous run exposed a test-design error where the test assumed all eight independent agents would close on the same price. The test was corrected to assert the intended invariants rather than force identical strategy outcomes.

## Audit conclusion
v31 is suitable as a controlled development branch, not as a declaration of funded-live readiness. The next release should add persistent state, a production worker/scheduler for continuous operation, real native market feeds, durable chart streaming, richer agent-specific policies, and a complete prediction-to-outcome learning/calibration loop. Live trading remains blocked until the existing data, reconciliation, execution, risk, and client-consent gates are independently proven.
