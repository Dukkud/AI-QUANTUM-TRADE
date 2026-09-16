# v34.4 — Gold Triangulation Evidence Engine

## Purpose
Add an independent cross-market relationship layer for XAUUSD, PAXG and XAUT without replacing the existing sources and without changing Q1-Q8 weights.

## Measurements
- synchronized price basis: PAXG/XAUUSD and XAUT/XAUUSD;
- return correlation: PAXG-XAUUSD, XAUT-XAUUSD, PAXG-XAUT;
- lead/lag correlation over ±3 observations;
- timestamp integrity and positive-price validation.

## Evidence policy
The engine returns `EVIDENCE_ONLY`. It cannot emit an order, change an agent weight, or enable live execution. Binance PAXG/XAUT remain market-data evidence, not native XAUUSD and not native Q3 order flow.

## Required next evidence gate
Before this layer can influence agent weights:
1. deployment connectivity for Binance PAXG/XAUT;
2. independent XAUUSD source with matching timestamps;
3. gap/duplicate and clock-alignment validation;
4. rolling and regime-conditioned correlation stability;
5. lead/lag stability on untouched OOS windows;
6. incremental predictive value versus the XAUUSD-only baseline;
7. net-cost validation and anti-overfit checks;
8. forward paper observation with settlement and attribution.

A high correlation by itself is not evidence of predictive value or causality.

## Learning continuity
Q1-Q8, Paper World, Evidence Machine, skill evidence, attribution, calibration and hourly telemetry are not paused. This module is an additive observational feature layer.

## Safety
`research_only=true`, `live_execution=false`, `weight_update=false`.
