"""AI-QUANTUM Q1-Q8 decision layer.

Research/paper only. This module deliberately fails closed when required market,
macro, quote, ML, or risk evidence is unavailable. It does not place orders.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from math import isfinite, sqrt
from statistics import mean
from typing import Any, Dict, Iterable, List, Optional

AGENT_NAMES = {
    "Q1": "Market Regime", "Q2": "Structure & Liquidity", "Q3": "Order Flow",
    "Q4": "Quant / Statistics", "Q5": "Geometry / Cycles", "Q6": "Macro / News / Geopolitics",
    "Q7": "ML / Pattern", "Q8": "Risk / Veto",
}

@dataclass(frozen=True)
class AgentDecision:
    agent: str
    function: str
    status: str
    decision: str
    confidence: float
    evidence: Dict[str, Any]
    reasons: List[str]
    data_quality: str = "OK"

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)

def _clamp(x: float, lo=0.0, hi=1.0) -> float:
    return max(lo, min(hi, float(x)))

def _bars(ctx: Dict[str, Any]) -> List[Dict[str, float]]:
    return list(ctx.get("bars") or [])

def _close_series(ctx: Dict[str, Any]) -> List[float]:
    return [float(b["close"]) for b in _bars(ctx) if "close" in b]

def _ema(xs: List[float], n: int) -> float:
    if not xs: raise ValueError("no prices")
    alpha = 2.0 / (n + 1.0); e = xs[0]
    for x in xs[1:]: e = alpha*x + (1-alpha)*e
    return e

def _atr(ctx: Dict[str, Any], n: int = 14) -> Optional[float]:
    bs = _bars(ctx)
    if len(bs) < 2: return None
    trs=[]; prev=float(bs[0]["close"])
    for b in bs[1:]:
        h,l=float(b["high"]),float(b["low"]); trs.append(max(h-l,abs(h-prev),abs(l-prev))); prev=float(b["close"])
    return mean(trs[-n:]) if trs else None

def q1_market_regime(ctx: Dict[str, Any]) -> AgentDecision:
    xs=_close_series(ctx)
    if len(xs)<50:
        return AgentDecision("Q1",AGENT_NAMES["Q1"],"INSUFFICIENT_DATA","HOLD",0.0,{"bars":len(xs)},["Need >=50 causal closes"] ,"INSUFFICIENT")
    e20,e50=_ema(xs,20),_ema(xs,50); atr=_atr(ctx); px=xs[-1]
    vol=(atr/px) if atr and px else 0.0
    slope=(xs[-1]-xs[-21])/xs[-21] if xs[-21] else 0.0
    if abs(slope)<0.0015: regime="RANGE"
    elif slope>0 and e20>e50: regime="TREND_UP"
    elif slope<0 and e20<e50: regime="TREND_DOWN"
    else: regime="TRANSITION"
    conf=_clamp(abs(slope)*100 + abs(e20-e50)/px*20)
    return AgentDecision("Q1",AGENT_NAMES["Q1"],"ACTIVE","BIAS_UP" if regime=="TREND_UP" else "BIAS_DOWN" if regime=="TREND_DOWN" else "HOLD",conf,{"regime":regime,"ema20":e20,"ema50":e50,"atr":atr,"atr_pct":vol,"slope20":slope},[f"Regime={regime}"])

def q2_structure(ctx: Dict[str, Any]) -> AgentDecision:
    bs=_bars(ctx)
    if len(bs)<20: return AgentDecision("Q2",AGENT_NAMES["Q2"],"INSUFFICIENT_DATA","HOLD",0.0,{"bars":len(bs)},["Need >=20 bars"],"INSUFFICIENT")
    highs=[float(b["high"]) for b in bs]; lows=[float(b["low"]) for b in bs]; mid=len(bs)//2
    old_h=max(highs[:mid]); new_h=max(highs[mid:]); old_l=min(lows[:mid]); new_l=min(lows[mid:])
    bos_up=new_h>old_h; bos_dn=new_l<old_l
    last=float(bs[-1]["close"]); sweep_up=last>old_h; sweep_dn=last<old_l
    if bos_up and not bos_dn: dec="BIAS_UP"
    elif bos_dn and not bos_up: dec="BIAS_DOWN"
    else: dec="HOLD"
    return AgentDecision("Q2",AGENT_NAMES["Q2"],"ACTIVE",dec,_clamp((abs(new_h-old_h)+abs(new_l-old_l))/(last*0.01)),{"BOS_UP":bos_up,"BOS_DOWN":bos_dn,"liquidity_sweep_up":sweep_up,"liquidity_sweep_down":sweep_dn,"range_high":old_h,"range_low":old_l},["Causal half-sample structure comparison"])

def q3_order_flow(ctx: Dict[str, Any]) -> AgentDecision:
    bid,ask=ctx.get("bid"),ctx.get("ask"); vol=ctx.get("buy_volume"),ctx.get("sell_volume")
    if bid is None or ask is None or vol is None or vol[0] is None or vol[1] is None:
        return AgentDecision("Q3",AGENT_NAMES["Q3"],"DATA_UNAVAILABLE","HOLD",0.0,{"native_bid_ask":bool(bid is not None and ask is not None),"native_volume":bool(vol)},["Native bid/ask and buy/sell flow are required; synthetic order flow is forbidden"],"UNAVAILABLE")
    spread=float(ask)-float(bid); buy,sell=float(vol[0]),float(vol[1]); total=buy+sell
    imb=(buy-sell)/total if total else 0.0
    return AgentDecision("Q3",AGENT_NAMES["Q3"],"ACTIVE","BIAS_UP" if imb>0.05 else "BIAS_DOWN" if imb<-0.05 else "HOLD",_clamp(abs(imb)*2),{"spread":spread,"imbalance":imb},["Native quote/flow evidence"])

def q4_quant(ctx: Dict[str, Any]) -> AgentDecision:
    rs=[float(x) for x in (ctx.get("historical_r") or [])]
    p=float(ctx.get("predicted_probability",0.5)); cost=float(ctx.get("cost_r_per_trade",0.0))
    if len(rs)<30: return AgentDecision("Q4",AGENT_NAMES["Q4"],"INSUFFICIENT_DATA","HOLD",0.0,{"trades":len(rs)},["Need >=30 realized R observations for expectancy gate"],"INSUFFICIENT")
    wins=[r for r in rs if r>0]; losses=[-r for r in rs if r<0]; pw=len(wins)/len(rs); aw=mean(wins) if wins else 0.0; al=mean(losses) if losses else 0.0
    ev=p*aw-(1-p)*al-cost
    realized=mean(rs)-cost
    variance=mean([(r-mean(rs))**2 for r in rs]) if rs else 0.0
    return AgentDecision("Q4",AGENT_NAMES["Q4"],"ACTIVE","TRADE" if ev>0 else "HOLD",_clamp(1/(1+sqrt(variance))),{"p":p,"avg_win":aw,"avg_loss":al,"ev_net":ev,"realized_mean_net":realized,"variance":variance,"win_rate":pw},["EV_net > 0 required"] if ev<=0 else ["Positive net expectancy"])

def q5_geometry(ctx: Dict[str, Any]) -> AgentDecision:
    xs=_close_series(ctx)
    if len(xs)<34: return AgentDecision("Q5",AGENT_NAMES["Q5"],"INSUFFICIENT_DATA","HOLD",0.0,{"bars":len(xs)},["Need >=34 bars for geometry/cycle baseline"],"INSUFFICIENT")
    hi=max(xs[-34:]); lo=min(xs[-34:]); px=xs[-1]; span=hi-lo
    pos=(px-lo)/span if span else 0.5
    # Fibonacci geometry is evidence, not a standalone trade trigger.
    return AgentDecision("Q5",AGENT_NAMES["Q5"],"ACTIVE","BIAS_UP" if pos<0.382 else "BIAS_DOWN" if pos>0.618 else "HOLD",_clamp(abs(pos-0.5)*2),{"range_high":hi,"range_low":lo,"position":pos,"fib_382":lo+span*.382,"fib_618":lo+span*.618},["34-bar causal range geometry"])

def q6_macro(ctx: Dict[str, Any]) -> AgentDecision:
    if not ctx.get("macro_verified") or not ctx.get("news_verified"):
        return AgentDecision("Q6",AGENT_NAMES["Q6"],"DATA_UNAVAILABLE","HOLD",0.0,{"macro_verified":bool(ctx.get("macro_verified")),"news_verified":bool(ctx.get("news_verified"))},["Verified macro/news feed required; no invented geopolitical signal"],"UNAVAILABLE")
    risk=str(ctx.get("macro_risk","NORMAL")); bias=str(ctx.get("macro_bias","NEUTRAL"))
    dec="BIAS_UP" if bias=="UP" else "BIAS_DOWN" if bias=="DOWN" else "HOLD"
    return AgentDecision("Q6",AGENT_NAMES["Q6"],"ACTIVE",dec,_clamp(float(ctx.get("macro_confidence",0.5))),{"risk":risk,"bias":bias,"dxy":ctx.get("dxy"),"yields":ctx.get("yields")},["Verified macro/news evidence"])

def q7_ml(ctx: Dict[str, Any]) -> AgentDecision:
    model=ctx.get("model_version"); prob=ctx.get("ml_probability"); calibrated=ctx.get("ml_calibrated",False)
    if not model or prob is None or not calibrated:
        return AgentDecision("Q7",AGENT_NAMES["Q7"],"DATA_UNAVAILABLE","HOLD",0.0,{"model_version":model,"calibrated":calibrated},["Versioned calibrated model and dataset required"],"UNAVAILABLE")
    p=float(prob); dec="BIAS_UP" if p>=0.55 else "BIAS_DOWN" if p<=0.45 else "HOLD"
    return AgentDecision("Q7",AGENT_NAMES["Q7"],"ACTIVE",dec,_clamp(abs(p-.5)*2),{"model_version":model,"probability_up":p,"dataset_fingerprint":ctx.get("dataset_fingerprint")},["Calibrated model probability"])

def q8_risk(ctx: Dict[str, Any], candidates: Optional[Iterable[AgentDecision]]=None) -> AgentDecision:
    vetoes=[]
    if not ctx.get("data_quality_ok",False): vetoes.append("DATA_QUALITY")
    if float(ctx.get("spread_pct",0.0))>float(ctx.get("max_spread_pct",0.001)): vetoes.append("SPREAD")
    if float(ctx.get("news_risk",0.0))>float(ctx.get("max_news_risk",0.8)): vetoes.append("NEWS_RISK")
    if float(ctx.get("drawdown_pct",0.0))>float(ctx.get("max_drawdown_pct",0.10)): vetoes.append("DRAWDOWN")
    if float(ctx.get("risk_pct",0.0))>float(ctx.get("max_risk_pct",0.01)): vetoes.append("RISK_LIMIT")
    if not ctx.get("account_ready",False): vetoes.append("ACCOUNT_NOT_READY")
    if ctx.get("emergency_stop",True): vetoes.append("EMERGENCY_STOP")
    if candidates:
        for c in candidates:
            if c.status in ("DATA_UNAVAILABLE","INSUFFICIENT_DATA"): vetoes.append(f"{c.agent}_EVIDENCE")
    dec="VETO" if vetoes else "CLEAR"
    return AgentDecision("Q8",AGENT_NAMES["Q8"],"ACTIVE",dec,1.0 if vetoes else 0.9,{"vetoes":vetoes},vetoes or ["Risk controls clear"])

def run_agent_council(ctx: Dict[str, Any]) -> Dict[str, Any]:
    agents=[q1_market_regime(ctx),q2_structure(ctx),q3_order_flow(ctx),q4_quant(ctx),q5_geometry(ctx),q6_macro(ctx),q7_ml(ctx)]
    risk=q8_risk(ctx,agents); agents.append(risk)
    hard_veto = risk.decision=="VETO"
    usable=[a for a in agents[:7] if a.decision in ("BIAS_UP","BIAS_DOWN","TRADE") and a.confidence>0]
    up=sum(a.confidence for a in usable if a.decision in ("BIAS_UP","TRADE")); down=sum(a.confidence for a in usable if a.decision=="BIAS_DOWN")
    decision="HOLD" if hard_veto or not usable else "LONG" if up>down*1.15 else "SHORT" if down>up*1.15 else "HOLD"
    return {"agents":[a.as_dict() for a in agents],"quantum_decision":decision,"hard_veto":hard_veto,"evidence_count":len(usable),"research_only":True,"live_execution":False}
