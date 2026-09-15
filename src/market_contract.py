"""Canonical market and signal contracts."""
from dataclasses import dataclass, asdict
from datetime import datetime

ASSETS = ('XAUUSD','BTCUSDT')
TIMEFRAMES = ('1M','5M','15M','30M','1H','2H','4H','1D','1W')

@dataclass(frozen=True)
class Signal:
    asset: str
    timeframe: str
    direction: str
    entry: float
    stop_loss: float
    tp1: float
    tp2: float
    tp3: float
    probability: float
    ev_net_r: float
    risk_pct: float
    confidence: float
    regime: str
    data_quality: float
    news_risk: float
    invalidation: str
    created_at_utc: str
    status: str = 'ACTIVE'
    def to_dict(self): return asdict(self)

def validate_scope(asset, timeframe):
    if asset not in ASSETS or timeframe not in TIMEFRAMES: raise ValueError('Unsupported market scope')
