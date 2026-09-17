# AI-QUANTUM VER2.0 Technical Specification Baseline

This document is the repository baseline for the full Word technical specification.

## System scope

Assets: XAUUSD and BTCUSDT.

Timeframes: 1M, 5M, 15M, 30M, 1H, 2H, 4H, 1D, 1W.

Strategic horizon: scenario analysis up to 24 months.

## Core flow

Source ingestion → validation → reconciliation → market state → Q1–Q7 analysis → adversarial debate → Quantum Core → Q8 Risk Gate → paper/result → Evidence Ledger → calibration/OOS → Q9 shadow learning → proposal/promotion controls.

## Decision contract

The system must preserve fail-closed decisions including APPROVE, APPROVE_REDUCED_SIZE, WAIT and NO_TRADE, with emergency protection. Live execution is not authorized by VER2.0 consolidation.

## Data governance

Every prediction/outcome requires lineage, timestamp, source, quality, regime and evaluation metadata. Spot and futures must remain explicitly separated where market microstructure differs.

## Knowledge graph

Q-GRAPH/Graphify may index architecture, dependencies, evidence references and provenance. It must not become a source of trading truth or execution authority.

## Security

Secrets remain environment-only; secret files are excluded from graph inventory; no credentials are committed; live trading remains blocked.

## ML governance

Parallel learning is allowed and encouraged for research, but promotion is gated by evidence, OOS stability, calibration, multiple-testing controls, security and risk.
