from dataclasses import dataclass
REGIMES=("TREND","RANGE","HIGH_VOLATILITY","LOW_VOLATILITY","NEWS_SHOCK","LIQUIDITY_STRESS")
@dataclass(frozen=True)
class ReplayCase:
    asset:str; timeframe:str; regime:str; score:float
def replay(cases:tuple[ReplayCase,...])->dict[str,float]:
    if any(c.regime not in REGIMES for c in cases): raise ValueError("unknown_regime")
    out={}
    for c in cases: out[c.regime]=out.get(c.regime,0.0)+c.score
    return out
