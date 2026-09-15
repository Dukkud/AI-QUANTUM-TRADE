# AI-QUANTUM-TRADE v33.5–v33.9 Evidence Machine

## Objective
Accumulate reproducible evidence continuously while Q1–Q8 paper learning continues. Evidence collection is shadow/observational and never enables live execution.

## Milestones
- **v33.5 Persistent Agent Ledger:** Q1–Q8 attribution survives process restart through append-only JSONL.
- **v33.6 Factual Trade Settlement:** paper trades expose opened_at, risk_cash, outcome_R, MAE_R and MFE_R; closed paper trades settle the corresponding agent evidence records.
- **v33.7 Calibration Ledger:** versioned ML predictions and one-step causal outcomes persist; Brier and Brier history are reproducible.
- **v33.8 Evidence Analytics:** attribution records are exposed to descriptive analytics and integrity endpoints.
- **v33.9 Forward-Paper Foundation:** the combined chain supports ongoing forward paper observation without pausing training.

## Integrity
Evidence JSONL records use a chained SHA-256 field. Integrity verification reports whether the append-only chain is internally consistent. This is tamper-evident, not a cryptographic external attestation.

## Learning continuity
No evidence requirement is used to stop Q1–Q8 learning. Missing Q3/Q6/Q7 evidence remains explicitly unavailable. Paper execution remains independent.

## Metrics now measurable
Trades, P&L, win rate, profit factor/EV where upstream data supports them, drawdown, MAE/MFE, Brier, agent weights, regime, learning state, loss debt, quarantine, errors, gate state and hour-over-hour telemetry.

## Important limitation
The ML Brier implementation currently evaluates the declared prediction against the next observed price direction. It is a causal calibration measure, not a claim of strategy profitability. Forward-paper validation requires sufficient real market observations, multiple regimes, realistic execution costs and pre-declared acceptance criteria.

## Safety
`research_only=true` and `live_execution=false` remain hard properties of the evidence layer. No evidence endpoint can authorize a live order.
