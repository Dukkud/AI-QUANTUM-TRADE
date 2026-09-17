"""Canonical AI-QUANTUM agent registry for VER2.0.

The registry is a control-plane contract. It does not execute trades or mutate
production weights. Q1-Q9 are the active agent set; Quantum Core remains a
coordination layer, not an additional agent.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class AgentSpec:
    agent_id: str
    name: str
    role: str
    mode: str
    production_mutation: bool = False


ACTIVE_AGENTS: Tuple[AgentSpec, ...] = (
    AgentSpec("Q1", "Market State", "regime/trend/volatility state", "ANALYZE"),
    AgentSpec("Q2", "Structure & Liquidity", "market structure, liquidity, SMC", "ANALYZE"),
    AgentSpec("Q3", "Order Flow", "delta/CVD/imbalance/absorption", "ANALYZE"),
    AgentSpec("Q4", "Quant Mathematics", "statistics, EV, distributions, robustness", "ANALYZE"),
    AgentSpec("Q5", "Geometry & Cycles", "Fibonacci, ratios, cycles, time/price geometry", "ANALYZE"),
    AgentSpec("Q6", "Macro / News / Geopolitics", "macro, news, cross-asset and event risk", "ANALYZE"),
    AgentSpec("Q7", "ML / Pattern Engine", "ML, pattern, anomaly, regime and analogue research", "TRAIN_SHADOW"),
    AgentSpec("Q8", "Risk & Decision", "risk gate and fail-closed decision", "GATE"),
    AgentSpec("Q9", "Self-Learning", "self-learning, evolution and learning orchestration", "TRAIN_SHADOW"),
)


def required_agent_ids() -> tuple[str, ...]:
    return tuple(agent.agent_id for agent in ACTIVE_AGENTS)


def validate_agent_registry() -> tuple[str, ...]:
    errors: list[str] = []
    ids = required_agent_ids()
    if ids != tuple(f"Q{i}" for i in range(1, 10)):
        errors.append("ACTIVE_AGENT_SET_MUST_BE_Q1_Q9")
    if any(agent.production_mutation for agent in ACTIVE_AGENTS):
        errors.append("AGENT_REGISTRY_MUST_NOT_AUTHORIZE_PRODUCTION_MUTATION")
    if ACTIVE_AGENTS[7].mode != "GATE":
        errors.append("Q8_MUST_REMAIN_RISK_GATE")
    if ACTIVE_AGENTS[8].mode != "TRAIN_SHADOW":
        errors.append("Q9_MUST_REMAIN_SHADOW_TRAINING")
    return tuple(errors)
