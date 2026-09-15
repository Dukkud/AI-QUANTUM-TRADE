"""v33 proven-research candidate gate. Never enables live trading."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from math import sqrt
from statistics import mean
from typing import Dict, List

@dataclass(frozen=True)
class ExecutionModel:
    commission_r: float = 0.0
    slippage_r: float = 0.0
    spread_r: float = 0.0
    latency_r: float = 0.0
    @property
    def total_cost_r(self): return self.commission_r+self.slippage_r+self.spread_r+self.latency_r

@dataclass(frozen=True)
class CandidateResult:
    passed: bool
    status: str
    reasons: List[str]
    metrics: Dict[str, float]
    live_execution: bool = False
    research_only: bool = True

def metrics(rs: List[float], model: ExecutionModel) -> Dict[str,float]:
    if not rs: return {"trades":0,"net_expectancy_r":0.0,"max_drawdown_r":0.0,"profit_factor":0.0}
    net=[r-model.total_cost_r for r in rs]; eq=peak=0.0; dd=0.0
    wins=sum(x for x in net if x>0); losses=-sum(x for x in net if x<0)
    for x in net:
        eq+=x; peak=max(peak,eq); dd=max(dd,peak-eq)
    return {"trades":float(len(net)),"net_expectancy_r":mean(net),"max_drawdown_r":dd,"profit_factor":wins/losses if losses else float("inf"),"win_rate":sum(x>0 for x in net)/len(net)}

def brier(prob: List[float], outcomes: List[int]) -> float:
    if not prob or len(prob)!=len(outcomes): return 1.0
    return mean([(float(p)-int(y))**2 for p,y in zip(prob,outcomes)])

def walk_forward(rs: List[float], train: int=100, oos: int=50) -> List[Dict[str,float]]:
    out=[]; i=0
    while i+train+oos<=len(rs):
        test=rs[i+train:i+train+oos]; out.append({"window":len(out)+1,"oos_expectancy_r":mean(test) if test else 0.0,"oos_trades":float(len(test))}); i+=oos
    return out

def regime_robustness(rows: List[Dict[str,object]], model: ExecutionModel) -> Dict[str,object]:
    groups={}
    for r in rows: groups.setdefault(str(r.get("regime","UNKNOWN")),[]).append(float(r["pnl_r"]))
    result={k:metrics(v,model) for k,v in groups.items()}
    positive=sum(1 for v in result.values() if v["net_expectancy_r"]>0)
    return {"regimes":result,"positive_regimes":positive,"total_regimes":len(result),"robust":positive==len(result) and len(result)>0}

def agent_attribution(rows: List[Dict[str,object]], model: ExecutionModel) -> Dict[str,object]:
    groups={}
    for r in rows: groups.setdefault(str(r.get("agent","UNKNOWN")),[]).append(float(r["pnl_r"]))
    return {k:metrics(v,model) for k,v in groups.items()}

def anti_overfit(rows: List[Dict[str,object]]) -> Dict[str,object]:
    n=len(rows); unique=len({str(r.get("window","")) for r in rows});
    return {"observations":n,"unique_windows":unique,"leakage_flag":any(bool(r.get("future_data_used",False)) for r in rows),"minimum_diversity_pass":unique>=3 and n>=90}

def candidate_gate(oos: List[float], model: ExecutionModel, *, min_trades=30, min_expectancy_r=0.0, max_drawdown_r=10.0, max_brier=0.25, brier_score=1.0, min_positive_windows=2, robustness: bool=False, anti_overfit_pass: bool=False) -> CandidateResult:
    m=metrics(oos,model); reasons=[]
    if m["trades"]<min_trades: reasons.append("INSUFFICIENT_OOS_TRADES")
    if m["net_expectancy_r"]<=min_expectancy_r: reasons.append("NON_POSITIVE_NET_EXPECTANCY")
    if m["max_drawdown_r"]>max_drawdown_r: reasons.append("DRAWDOWN_LIMIT")
    if brier_score>max_brier: reasons.append("CALIBRATION_LIMIT")
    if len([x for x in oos if x-model.total_cost_r>0])<min_positive_windows: reasons.append("INSUFFICIENT_POSITIVE_OBSERVATIONS")
    if not robustness: reasons.append("REGIME_ROBUSTNESS_FAIL")
    if not anti_overfit_pass: reasons.append("ANTI_OVERFIT_FAIL")
    passed=not reasons
    return CandidateResult(passed,"PROMOTE_RESEARCH" if passed else "HOLD",reasons,m)

def run_v33(rows: List[Dict[str,object]], model: ExecutionModel=ExecutionModel(), *, probabilities=None, outcomes=None) -> Dict[str,object]:
    oos=[float(r["pnl_r"]) for r in rows if r.get("oos",True)]
    wf=walk_forward(oos); rb=regime_robustness(rows,model); attr=agent_attribution(rows,model); ao=anti_overfit(rows)
    bs=brier(list(probabilities or []),list(outcomes or [])) if probabilities is not None and outcomes is not None else 1.0
    gate=candidate_gate(oos,model,brier_score=bs,robustness=bool(rb["robust"]),anti_overfit_pass=not ao["leakage_flag"] and bool(ao["minimum_diversity_pass"]))
    return {"version":"33.0.0","gate":asdict(gate),"walk_forward":wf,"regime_robustness":rb,"agent_attribution":attr,"anti_overfit":ao,"calibration_brier":bs,"research_only":True,"live_execution":False}
