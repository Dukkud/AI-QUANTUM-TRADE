"""Forward-paper evidence accumulator. Research-only; never promotes to live."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import List, Optional

@dataclass
class ForwardObservation:
    timestamp: str
    asset: str
    timeframe: str
    decision: str
    outcome_r: Optional[float] = None
    cost_r: float = 0.0
    regime: str = 'UNKNOWN'

class ForwardPaperValidator:
    def __init__(self): self.rows: List[ForwardObservation] = []
    def observe(self, row: ForwardObservation) -> None: self.rows.append(row)
    def settle(self, timestamp: str, asset: str, outcome_r: float) -> int:
        n=0
        for r in self.rows:
            if r.timestamp==timestamp and r.asset==asset and r.outcome_r is None:
                r.outcome_r=float(outcome_r); n+=1
        return n
    def metrics(self, min_trades: int = 30) -> dict:
        settled=[r for r in self.rows if r.outcome_r is not None and r.decision in {'LONG','SHORT','TRADE'}]
        net=[float(r.outcome_r)-float(r.cost_r) for r in settled]
        wins=sum(x>0 for x in net); gross=sum(net)
        peak=equity=max_dd=0.0
        for x in net:
            equity+=x; peak=max(peak,equity); max_dd=max(max_dd,peak-equity)
        gains=sum(x for x in net if x>0); losses=-sum(x for x in net if x<0)
        return {'research_only':True,'live_execution':False,'observations':len(self.rows),'settled_trades':len(settled),
                'ready_for_statistical_review':len(settled)>=min_trades,'net_pnl_r':gross,
                'win_rate':wins/len(net) if net else None,'profit_factor':gains/losses if losses else None,
                'max_drawdown_r':max_dd,'mean_net_r':gross/len(net) if net else None}
    def window_metrics(self, size: int = 100, min_trades: int = 30) -> List[dict]:
        if size<1: raise ValueError('size must be positive')
        rows=[r for r in self.rows if r.outcome_r is not None]
        return [ForwardPaperValidator._metric_rows(rows[i:i+size],min_trades) for i in range(0,max(0,len(rows)-size+1),size)]
    @staticmethod
    def _metric_rows(rows,min_trades):
        net=[float(r.outcome_r)-float(r.cost_r) for r in rows]; gains=sum(x for x in net if x>0); losses=-sum(x for x in net if x<0)
        return {'trades':len(net),'mean_net_r':sum(net)/len(net) if net else None,'profit_factor':gains/losses if losses else None,'ready_for_statistical_review':len(net)>=min_trades}
    def snapshot(self): return {'research_only':True,'live_execution':False,'rows':len(self.rows),'metrics':self.metrics(),'windows':self.window_metrics()}
