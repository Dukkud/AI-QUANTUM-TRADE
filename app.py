from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI

from src.adaptive_engine import AdaptiveEngine
from src.ai_quantum_core import QuantumCore, TradeCandidate
from src.edge_validation import ResearchTrade, feature_attribution, metrics, validation_gate, walk_forward
from src.evidence_gate import EvidenceRequirements, evidence_gate
from src.github_integrations import integration_registry
from src.github_integrations.pine_reference import validate_script
from src.github_integrations.xau_research import features as xau_features
from src.live_gate import ClientLiveGate
from src.market_replay import coerce_bar, dataset_fingerprint, replay, validate_dataset
from src.paper_world import PaperWorld
from src.realtime_api import normalize_tick, realtime_policy, source_status
from src.realtime_market import MarketTick
from src.realtime_training import RealtimeTrainingPolicy
from src.risk_engine import RiskEngine
from src.agent_decision_layer import run_agent_council
from src.v33_candidate_gate import ExecutionModel, run_v33

APP_VERSION = "33.0.0"
app = FastAPI(title="AI-QUANTUM-TRADE", version=APP_VERSION)
core = QuantumCore(); risk = RiskEngine(); adaptive = AdaptiveEngine(); paper = PaperWorld(); live_gate = ClientLiveGate(); training_policy = RealtimeTrainingPolicy()

@app.get("/health")
def health() -> dict[str, Any]:
    return {"status":"ok","mode":"paper","training_mode":training_policy.mode,"live_trading":False,"emergency_stop":True,"version":APP_VERSION,"github_integrations":"enabled_research_only","edge_validation":"research_only","evidence_gate":"fail_closed_research_only","market_replay":"deterministic_research_only","agent_decision_layer":"q1-q8_research_only","v33_candidate":"research_only"}

@app.get("/state")
def state() -> dict[str, Any]:
    return {"utc":datetime.now(timezone.utc).isoformat(),"assets":["XAUUSD","BTCUSDT"],"timeframes":list(training_policy.target_timeframes),"agent_weights":adaptive.weights(),"realtime_training":training_policy.snapshot(),"source_status":source_status(),"paper_world":paper.snapshot(),"github_integrations":integration_registry(),"edge_validation":{"research_only":True,"live_execution":False},"evidence_gate":{"research_only":True,"live_gate_enablement":False},"market_replay":{"research_only":True,"live_execution":False},"agent_decision_layer":{"research_only":True,"live_execution":False},"v33_candidate":{"research_only":True,"live_execution":False}}

@app.get("/integrations/github")
def github_integrations() -> dict[str, object]: return integration_registry()

@app.post("/integrations/pine/validate")
def validate_pine(payload: dict[str, Any]) -> dict[str, object]:
    result=validate_script(str(payload.get("script","")))
    return {"ok":result.ok,"errors":list(result.errors),"warnings":list(result.warnings),"matched_review_terms":list(result.matched_review_terms),"research_only":True}

@app.post("/integrations/xau/features")
def xau_feature_endpoint(payload: dict[str, Any]) -> dict[str, object]: return xau_features(payload.get("bars",[]))

@app.post("/research/agent-council")
def agent_council_endpoint(payload: dict[str, Any]) -> dict[str, object]: return run_agent_council(payload)

@app.post("/research/v33-candidate")
def v33_candidate_endpoint(payload: dict[str, Any]) -> dict[str, object]:
    model=ExecutionModel(float(payload.get("commission_r",0)),float(payload.get("slippage_r",0)),float(payload.get("spread_r",0)),float(payload.get("latency_r",0)))
    return run_v33(list(payload.get("trades",[])),model,probabilities=payload.get("probabilities"),outcomes=payload.get("outcomes"))

@app.post("/research/edge-validation")
def edge_validation_endpoint(payload: dict[str, Any]) -> dict[str, object]:
    cost_r=float(payload.get("cost_r_per_trade",0.0)); response={"research_only":True,"live_execution":False,"cost_r_per_trade":cost_r}
    if payload.get("variants"):
        response["feature_attribution"]=feature_attribution({str(n):rows for n,rows in payload["variants"].items()},cost_r)
    if payload.get("trades"):
        trades=[ResearchTrade(float(r["pnl_r"]),float(r.get("predicted_probability",0.5)),str(r.get("feature_group","baseline"))) for r in payload["trades"]]
        response["metrics"]=metrics(trades,cost_r).as_dict(); response["walk_forward"]=walk_forward(trades,int(payload.get("train_size",20)),int(payload.get("validation_size",10)),int(payload.get("oos_size",10)),cost_r)
        response["gate"]=validation_gate([w["oos"] for w in response["walk_forward"]],min_trades=int(payload.get("min_trades",30)),min_expectancy_r=float(payload.get("min_expectancy_r",0.0)),max_drawdown_r=float(payload.get("max_drawdown_r",10.0)),max_brier=float(payload.get("max_brier",0.25)))
    return response

@app.post("/research/evidence-gate")
def evidence_gate_endpoint(payload: dict[str, Any]) -> dict[str, object]:
    ep=payload.get("evidence",{}); evidence=EvidenceRequirements(**{k:bool(ep.get(k,False)) for k in EvidenceRequirements.__dataclass_fields__}); return evidence_gate(evidence,payload.get("oos_metrics"))

@app.post("/research/market-replay")
def market_replay_endpoint(payload: dict[str, Any]) -> dict[str, object]:
    rows=payload.get("bars",[]); validation=validate_dataset(rows); response={"research_only":True,"live_execution":False,"validation":validation}
    if validation["valid"]:
        bars=[coerce_bar(row) for row in rows]; response["dataset_fingerprint"]=dataset_fingerprint(bars); response["events"]=replay(bars)
    return response

@app.get("/realtime/policy")
def realtime_policy_endpoint() -> dict[str, Any]: return realtime_policy()

@app.get("/realtime/status")
def realtime_status() -> dict[str, Any]:
    status=source_status(); return {"policy":training_policy.snapshot(),"sources":status,"external_connection_verified":status["external_connection_verified_in_deployment"],"execution":"PAPER_ONLY","live_orders":False}

@app.post("/realtime/tick")
def realtime_tick(payload: dict[str, Any]) -> dict[str, Any]:
    tick=MarketTick(venue=str(payload["venue"]),symbol=str(payload["symbol"]),bid=float(payload["bid"]) if payload.get("bid") is not None else None,ask=float(payload["ask"]) if payload.get("ask") is not None else None,last=float(payload["last"]) if payload.get("last") is not None else None,volume=float(payload["volume"]) if payload.get("volume") is not None else None,exchange_ts_ms=int(payload["exchange_ts_ms"]) if payload.get("exchange_ts_ms") is not None else None,received_ts_ms=int(payload.get("received_ts_ms",datetime.now(timezone.utc).timestamp()*1000)),stream=str(payload.get("stream","normalized")),training_only=True)
    price=tick.last
    if price is None:
        if tick.bid is not None and tick.ask is not None: price=(tick.bid+tick.ask)/2.0
        elif tick.bid is not None: price=tick.bid
        elif tick.ask is not None: price=tick.ask
    if price is None or price<=0: raise ValueError("tick requires a positive last price or bid/ask")
    return {"tick":normalize_tick(tick),"paper":paper.tick(tick.symbol,price,payload.get("timestamp"),payload.get("prev")),"live_execution":False}

@app.post("/decision")
def decision(payload: dict[str, Any]) -> dict[str, Any]:
    candidate=TradeCandidate(**payload); result=core.decide(candidate); return {"decision":result,"rr":candidate.rr,"ev_r":candidate.ev_r,"risk_pct":risk.position_risk_pct(candidate.probability,result=="APPROVE_REDUCED_SIZE")}

@app.get("/paper/world")
def paper_world() -> dict[str, Any]: return paper.snapshot()
@app.post("/paper/tick")
def paper_tick(payload: dict[str, Any]) -> dict[str, Any]: return paper.tick(payload["asset"],float(payload["price"]),payload.get("timestamp"),payload.get("prev"))
@app.get("/paper/agents")
def paper_agents() -> dict[str, Any]: return paper.agent_report()
@app.get("/paper/trades")
def paper_trades() -> dict[str, Any]: return {key:wallet.history for key,wallet in paper.wallets.items()}
@app.get("/paper/lines")
def paper_lines() -> list[dict[str, Any]]: return paper.lines[-500:]
@app.get("/paper/report")
def paper_report() -> dict[str, Any]: return {"generated_at":datetime.now(timezone.utc).isoformat(),"agents":paper.agent_report(),"market":paper.market,"tick_count":paper.tick_count,"training_policy":training_policy.snapshot()}

@app.post("/account/register")
def register_account(payload: dict[str, Any]) -> dict[str, Any]:
    account=live_gate.register(payload["account_id"],payload["provider"]); return {"account_id":account.account_id,"provider":account.provider,"verified":account.verified,"trading_confirmed":account.trading_confirmed}
@app.post("/account/{account_id}/verify")
def verify_account(account_id: str) -> dict[str, Any]: live_gate.verify(account_id); return {"account_id":account_id,"verified":True}
@app.post("/account/{account_id}/confirm-trading")
def confirm_trading(account_id: str) -> dict[str, Any]: live_gate.confirm_trading(account_id); return {"account_id":account_id,"trading_confirmed":True}
@app.post("/live/gate")
def live_gate_status(payload: dict[str, Any]) -> dict[str, Any]: return {"can_trade_live":live_gate.can_trade_live(payload["account_id"],payload.get("safety_gates",{}),payload.get("live_trading",False),payload.get("emergency_stop",True))}
