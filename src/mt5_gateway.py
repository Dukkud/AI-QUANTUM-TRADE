"""MT5 native quote boundary. Credentials remain outside the repository."""
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class Tick:
    time_utc: datetime
    bid: float
    ask: float
    last: float
    volume: float

class MT5Gateway:
    def __init__(self): self.connected=False
    def connect(self):
        try:
            import MetaTrader5 as mt5
        except ImportError:
            return False
        self.connected = bool(mt5.initialize())
        return self.connected
    def ticks(self, symbol: str, start, end):
        if not self.connected: raise RuntimeError('MT5 gateway is not connected')
        import MetaTrader5 as mt5
        return mt5.copy_ticks_range(symbol, start, end, mt5.COPY_TICKS_ALL)
    def shutdown(self):
        if self.connected:
            import MetaTrader5 as mt5
            mt5.shutdown(); self.connected=False
