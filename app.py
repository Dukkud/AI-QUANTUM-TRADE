from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI

from src.adaptive_engine import AdaptiveEngine
from src.ai_quantum_core import QuantumCore, TradeCandidate
from src.github_integrations import integration_registry
from src.github_integrations.pine_reference import validate_script
from src.github_integrations.xau_research import features as xau_features
from src.live_gate import ClientLiveGate
from src.paper_world import PaperWorld
from src.realtime_api import normalize_tick, realtime_policy, source_status
from src.realtime_market import MarketTick
from src.realtime_training import RealtimeTrainingPolicy
from src.risk_engine import RiskEngine

APP_VERSION = "31.4.0"

app = FastAPI(title="AI-QUANTUM-TRADE", version=APP_VERSION)
core = QuantumCore()
risk = RiskEngine()
adaptive = AdaptiveEngine()
paper = PaperWorld()
live_gate = ClientLiveGate()
training_policy = RealtimeTrainingPolicy()


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "mode": "paper",
        "training_mode": training_policy.mode,
        "live_trading": False,
        "emergency_stop": True,
        "version": APP_VERSION,
        "github_integrations": "enabled_research_only",
    }


@app.get("/state")
def state() -> dict[str, Any]:
    return {
        "utc": datetime.now(timezone.utc).isoformat(),
        "assets": ["XAUUSD", "BTCUSDT"],
        "timeframes": list(training_policy.target_timeframes),
        "agent_weights": adaptive.weights(),
        "realtime_training": training_policy.snapshot(),
        "source_status": source_status(),
        "paper_world": paper.snapshot(),
        "github_integrations": integration_registry(),
    }


@app.get("/integrations/github")
def github_integrations() -> dict[str, object]:
    return integration_registry()


@app.post("/integrations/pine/validate")
def validate_pine(payload: dict[str, Any]) -> dict[str, object]:
    result = validate_script(str(payload.get("script", "")))
    return {
        "ok": result.ok,
        "errors": list(result.errors),
        "warnings": list(result.warnings),
        "matched_review_terms": list(result.matched_review_terms),
        "research_only": True,
    }


@app.post("/integrations/xau/features")
def xau_feature_endpoint(payload: dict[str, Any]) -> dict[str, object]:
    bars = payload.get("bars", [])
    result = xau_features(bars)
    return result


@app.get("/realtime/policy")
def realtime_policy_endpoint() -> dict[str, Any]:
    return realtime_policy()


@app.get("/realtime/status")
def realtime_status() -> dict[str, Any]:
    status = source_status()
    return {
        "policy": training_policy.snapshot(),
        "sources": status,
        "external_connection_verified": status["external_connection_verified_in_deployment"],
        "execution": "PAPER_ONLY",
        "live_orders": False,
    }


@app.post("/realtime/tick")
def realtime_tick(payload: dict[str, Any]) -> dict[str, Any]:
    """Ingest one normalized market tick into the paper world.

    This endpoint is intentionally an ingestion/training boundary. It never
    calls an exchange order endpoint and cannot enable live execution.
    """
    tick = MarketTick(
        venue=str(payload["venue"]),
        symbol=str(payload["symbol"]),
        bid=float(payload["bid"]) if payload.get("bid") is not None else None,
        ask=float(payload["ask"]) if payload.get("ask") is not None else None,
        last=float(payload["last"]) if payload.get("last") is not None else None,
        volume=float(payload["volume"]) if payload.get("volume") is not None else None,
        exchange_ts_ms=int(payload["exchange_ts_ms"]) if payload.get("exchange_ts_ms") is not None else None,
        received_ts_ms=int(payload.get("received_ts_ms", datetime.now(timezone.utc).timestamp() * 1000)),
        stream=str(payload.get("stream", "normalized")),
        training_only=True,
    )
    price = tick.last
    if price is None:
        if tick.bid is not None and tick.ask is not None:
            price = (tick.bid + tick.ask) / 2.0
        elif tick.bid is not None:
            price = tick.bid
        elif tick.ask is not None:
            price = tick.ask
    if price is None or price <= 0:
        raise ValueError("tick requires a positive last price or bid/ask")

    previous = payload.get("prev")
    snapshot = paper.tick(tick.symbol, price, payload.get("timestamp"), previous)
    envelope = normalize_tick(tick)
    return {"tick": envelope, "paper": snapshot, "live_execution": False}


@app.post("/decision")
def decision(payload: dict[str, Any]) -> dict[str, Any]:
    candidate = TradeCandidate(**payload)
    result = core.decide(candidate)
    return {
        "decision": result,
        "rr": candidate.rr,
        "ev_r": candidate.ev_r,
        "risk_pct": risk.position_risk_pct(candidate.probability, result == "APPROVE_REDUCED_SIZE"),
    }


@app.get("/paper/world")
def paper_world() -> dict[str, Any]:
    return paper.snapshot()


@app.post("/paper/tick")
def paper_tick(payload: dict[str, Any]) -> dict[str, Any]:
    return paper.tick(payload["asset"], float(payload["price"]), payload.get("timestamp"), payload.get("prev"))


@app.get("/paper/agents")
def paper_agents() -> dict[str, Any]:
    return paper.agent_report()


@app.get("/paper/trades")
def paper_trades() -> dict[str, Any]:
    return {key: wallet.history for key, wallet in paper.wallets.items()}


@app.get("/paper/lines")
def paper_lines() -> list[dict[str, Any]]:
    return paper.lines[-500:]


@app.get("/paper/report")
def paper_report() -> dict[str, Any]:
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "agents": paper.agent_report(),
        "market": paper.market,
        "tick_count": paper.tick_count,
        "training_policy": training_policy.snapshot(),
    }


@app.post("/account/register")
def register_account(payload: dict[str, Any]) -> dict[str, Any]:
    account = live_gate.register(payload["account_id"], payload["provider"])
    return {
        "account_id": account.account_id,
        "provider": account.provider,
        "verified": account.verified,
        "trading_confirmed": account.trading_confirmed,
    }


@app.post("/account/{account_id}/verify")
def verify_account(account_id: str) -> dict[str, Any]:
    live_gate.verify(account_id)
    return {"account_id": account_id, "verified": True}


@app.post("/account/{account_id}/confirm-trading")
def confirm_trading(account_id: str) -> dict[str, Any]:
    live_gate.confirm_trading(account_id)
    return {"account_id": account_id, "trading_confirmed": True}


@app.post("/live/gate")
def live_gate_status(payload: dict[str, Any]) -> dict[str, Any]:
    account_id = payload["account_id"]
    safety = payload.get("safety_gates", {})
    return {
        "can_trade_live": live_gate.can_trade_live(
            account_id,
            safety,
            payload.get("live_trading", False),
            payload.get("emergency_stop", True),
        )
    }
