"""Source adapters for AQ-MARKET and AQ-MACRO. External I/O remains injectable."""
from __future__ import annotations
from dataclasses import dataclass
@dataclass(frozen=True)
class MarketSnapshot:
    asset:str; timeframe:str; price:float; volume:float; timestamp:str; source_id:str
@dataclass(frozen=True)
class MacroEvent:
    event_id:str; name:str; severity:float; information_time:str; source_id:str
class MarketAdapter:
    def snapshot(self,**kwargs)->MarketSnapshot: return MarketSnapshot(**kwargs)
class MacroAdapter:
    def event(self,**kwargs)->MacroEvent: return MacroEvent(**kwargs)
