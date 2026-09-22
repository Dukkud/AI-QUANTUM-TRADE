"""Evaluation loop: outcome comparison and promotion proposal, never direct mutation."""
from __future__ import annotations
from dataclasses import dataclass
@dataclass(frozen=True)
class Evaluation:
    prediction_id:str
    realized_r:float
    brier:float
    sample_ok:bool
    oos_ok:bool
    calibration_ok:bool
    promotion_eligible:bool

def evaluate(*,prediction_id:str,realized_r:float,brier:float,sample_ok:bool,oos_ok:bool,calibration_ok:bool)->Evaluation:
    eligible=sample_ok and oos_ok and calibration_ok and realized_r>0
    return Evaluation(prediction_id,realized_r,brier,sample_ok,oos_ok,calibration_ok,eligible)
