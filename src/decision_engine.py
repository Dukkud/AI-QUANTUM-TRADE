"""Deterministic fail-closed AI-QUANTUM decision engine."""
def decide(*,data_quality:float,news_risk:float,rr:float,ev:float,agreement:float,probability:float)->str:
    if data_quality < .95: return "NO_TRADE"
    if news_risk >= .85: return "WAIT"
    if rr < 1.2 or ev <= 0: return "NO_TRADE"
    if agreement < .45: return "WAIT"
    if probability < .55: return "NO_TRADE"
    if agreement >= .70: return "APPROVE"
    return "APPROVE_REDUCED_SIZE"
