"""Persistent append-only hourly telemetry ledger for AI-QUANTUM paper/research mode."""
from __future__ import annotations
import json, os, tempfile
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List, Optional

SCHEMA_VERSION = "1.0"
DEFAULT_PATH = os.getenv("AI_QUANTUM_TELEMETRY_PATH", "data/hourly_telemetry.jsonl")

@dataclass
class HourlyTelemetry:
    hour_id: str
    generated_at: str
    trades: int
    pnl: float
    win_rate: float
    profit_factor: float
    ev: float
    drawdown: float
    mae: float
    mfe: float
    brier: Optional[float]
    weights: Dict[str, float] = field(default_factory=dict)
    regime: str = "UNKNOWN"
    learning: Dict[str, Any] = field(default_factory=dict)
    loss_debt: float = 0.0
    quarantine: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    gate: Dict[str, Any] = field(default_factory=dict)
    schema_version: str = SCHEMA_VERSION

class HourlyTelemetryLedger:
    """Durable JSONL ledger. Writes are atomic at the record level and append-only."""
    def __init__(self, path: str = DEFAULT_PATH):
        self.path=Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, record: HourlyTelemetry) -> HourlyTelemetry:
        line=json.dumps(asdict(record),ensure_ascii=False,sort_keys=True,separators=(",",":"))
        with self.path.open("a",encoding="utf-8") as f:
            f.write(line+"\n"); f.flush(); os.fsync(f.fileno())
        return record

    def read_all(self) -> List[HourlyTelemetry]:
        if not self.path.exists(): return []
        out=[]
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip(): out.append(HourlyTelemetry(**json.loads(line)))
        return out

    def latest(self) -> Optional[HourlyTelemetry]:
        rows=self.read_all(); return rows[-1] if rows else None

    def previous(self) -> Optional[HourlyTelemetry]:
        rows=self.read_all(); return rows[-2] if len(rows)>1 else None

    @staticmethod
    def compare(current: HourlyTelemetry, previous: Optional[HourlyTelemetry]) -> Dict[str, Any]:
        if previous is None: return {"available":False,"reason":"NO_PREVIOUS_HOUR"}
        def d(a,b): return round(float(a)-float(b),10)
        return {"available":True,"hour_n":current.hour_id,"hour_n_minus_1":previous.hour_id,
                "delta":{"trades":current.trades-previous.trades,"pnl":d(current.pnl,previous.pnl),"win_rate":d(current.win_rate,previous.win_rate),"profit_factor":d(current.profit_factor,previous.profit_factor),"ev":d(current.ev,previous.ev),"drawdown":d(current.drawdown,previous.drawdown),"mae":d(current.mae,previous.mae),"mfe":d(current.mfe,previous.mfe),"brier":None if current.brier is None or previous.brier is None else d(current.brier,previous.brier),"loss_debt":d(current.loss_debt,previous.loss_debt)},
                "weights_changed":current.weights!=previous.weights,"regime_changed":current.regime!=previous.regime,"learning_changed":current.learning!=previous.learning,"quarantine_changed":current.quarantine!=previous.quarantine,"errors_changed":current.errors!=previous.errors,"gate_changed":current.gate!=previous.gate}

def _trade_metrics(trades: List[Dict[str,Any]]) -> Dict[str,float]:
    rs=[float(t.get("pnl",0.0)) for t in trades]; wins=[x for x in rs if x>0]; losses=[-x for x in rs if x<0]
    pf=sum(wins)/sum(losses) if losses else (float("inf") if wins else 0.0)
    return {"trades":len(rs),"pnl":sum(rs),"win_rate":len(wins)/len(rs) if rs else 0.0,"profit_factor":pf,"ev":mean(rs) if rs else 0.0}

def build_hourly_record(*,hour_id: str, trades: List[Dict[str,Any]], weights=None, regime="UNKNOWN", learning=None, loss_debt=0.0, quarantine=None, errors=None, gate=None, brier=None, drawdown=0.0, mae=None, mfe=None, generated_at=None) -> HourlyTelemetry:
    m=_trade_metrics(trades)
    maes=[float(t["mae"]) for t in trades if t.get("mae") is not None]; mfes=[float(t["mfe"]) for t in trades if t.get("mfe") is not None]
    return HourlyTelemetry(hour_id=hour_id,generated_at=generated_at or datetime.now(timezone.utc).isoformat(),trades=m["trades"],pnl=m["pnl"],win_rate=m["win_rate"],profit_factor=m["profit_factor"],ev=m["ev"],drawdown=float(drawdown),mae=float(mean(maes) if mae is None and maes else mae or 0.0),mfe=float(mean(mfes) if mfe is None and mfes else mfe or 0.0),brier=brier,weights=dict(weights or {}),regime=str(regime),learning=dict(learning or {}),loss_debt=float(loss_debt),quarantine=dict(quarantine or {}),errors=list(errors or []),gate=dict(gate or {}))
