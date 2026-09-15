from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
import math

INITIAL_BALANCE = 1000.0
LOCK_DAYS = 5

AGENTS = {
    'Q1': 'Market State', 'Q2': 'Structure & Liquidity', 'Q3': 'Order Flow',
    'Q4': 'Quant Mathematics', 'Q5': 'Geometry & Cycles', 'Q6': 'Macro/News/Geopolitics',
    'Q7': 'ML/Pattern Engine', 'Q8': 'Risk'
}

@dataclass
class Position:
    agent: str
    asset: str
    direction: str
    entry: float
    stop: float
    target: float
    opened_at: str
    qty: float
    status: str = 'OPEN'
    exit: Optional[float] = None
    pnl: float = 0.0
    exit_reason: Optional[str] = None

@dataclass
class AgentWallet:
    agent: str
    name: str
    balance: float = INITIAL_BALANCE
    peak_balance: float = INITIAL_BALANCE
    wins: int = 0
    losses: int = 0
    trades: int = 0
    experience: float = 0.0
    locked_until: Optional[str] = None
    last_error: Optional[str] = None
    positions: List[Position] = field(default_factory=list)
    history: List[dict] = field(default_factory=list)

    @property
    def available(self):
        return self.balance

    @property
    def win_rate(self):
        return self.wins / self.trades if self.trades else 0.0

    def is_locked(self, now: datetime) -> bool:
        if not self.locked_until:
            return False
        return now < datetime.fromisoformat(self.locked_until)

class PaperWorld:
    """Deterministic virtual market world. It never calls a real broker."""
    def __init__(self):
        self.wallets = {k: AgentWallet(k, v) for k, v in AGENTS.items()}
        self.lines: List[dict] = []
        self.market: Dict[str, dict] = {}
        self.clock = datetime.now(timezone.utc)
        self.tick_count = 0

    def _signal(self, agent: str, asset: str, price: float, tick: dict):
        # v31 baseline policies are intentionally deterministic placeholders;
        # they provide a safe execution/experience framework for later model policies.
        prev = tick.get('prev', price)
        move = price - prev
        bias = (sum(ord(c) for c in agent + asset) % 3) - 1
        direction = 'LONG' if move * bias >= 0 else 'SHORT'
        if abs(move) < 1e-12:
            direction = 'LONG' if bias >= 0 else 'SHORT'
        distance = max(abs(price) * 0.002, 0.01)
        stop = price - distance if direction == 'LONG' else price + distance
        target = price + distance * 2.0 if direction == 'LONG' else price - distance * 2.0
        return direction, stop, target

    def _open(self, wallet: AgentWallet, asset: str, price: float, tick: dict):
        if wallet.is_locked(self.clock) or wallet.positions:
            return None
        direction, stop, target = self._signal(wallet.agent, asset, price, tick)
        risk_cash = wallet.balance * 0.01
        risk_per_unit = abs(price - stop)
        qty = risk_cash / risk_per_unit if risk_per_unit else 0.0
        pos = Position(wallet.agent, asset, direction, price, stop, target,
                       self.clock.isoformat(), qty)
        wallet.positions.append(pos)
        self.lines.append({'agent': wallet.agent, 'asset': asset, 'direction': direction,
                           'entry': price, 'stop_loss': stop, 'target': target,
                           'status': 'OPEN', 'opened_at': pos.opened_at})
        return pos

    def _close(self, wallet: AgentWallet, pos: Position, price: float, reason: str):
        if pos.status != 'OPEN':
            return
        raw = (price - pos.entry) * pos.qty
        if pos.direction == 'SHORT':
            raw = -raw
        pos.exit, pos.status, pos.pnl, pos.exit_reason = price, 'CLOSED', raw, reason
        wallet.balance += raw
        wallet.trades += 1
        if raw > 0:
            wallet.wins += 1
            wallet.experience += 1.0 + math.log1p(raw / INITIAL_BALANCE)
        else:
            wallet.losses += 1
            wallet.last_error = reason
            wallet.experience += 0.5
        wallet.peak_balance = max(wallet.peak_balance, wallet.balance)
        wallet.history.append({'asset': pos.asset, 'direction': pos.direction,
                               'entry': pos.entry, 'exit': price, 'pnl': raw,
                               'reason': reason, 'time': self.clock.isoformat()})
        if wallet.balance < 0:
            wallet.locked_until = (self.clock + timedelta(days=LOCK_DAYS)).isoformat()
            wallet.balance = 0.0

    def tick(self, asset: str, price: float, timestamp: Optional[str] = None, prev: Optional[float] = None):
        self.clock = datetime.fromisoformat(timestamp) if timestamp else datetime.now(timezone.utc)
        tick = {'prev': prev if prev is not None else price}
        self.market[asset] = {'price': price, 'time': self.clock.isoformat()}
        self.tick_count += 1
        for wallet in self.wallets.values():
            # Resolve positions first using exact SL/TP levels.
            for pos in list(wallet.positions):
                if pos.asset != asset or pos.status != 'OPEN':
                    continue
                hit_sl = price <= pos.stop if pos.direction == 'LONG' else price >= pos.stop
                hit_tp = price >= pos.target if pos.direction == 'LONG' else price <= pos.target
                if hit_sl:
                    self._close(wallet, pos, pos.stop, 'STOP_LOSS')
                elif hit_tp:
                    self._close(wallet, pos, pos.target, 'TAKE_PROFIT')
            wallet.positions = [p for p in wallet.positions if p.status == 'OPEN']
            if not wallet.positions and not wallet.is_locked(self.clock):
                self._open(wallet, asset, price, tick)
        return self.snapshot()

    def daily_reset(self, agent: str):
        wallet = self.wallets[agent]
        if wallet.balance < INITIAL_BALANCE and not wallet.positions:
            wallet.balance = INITIAL_BALANCE
            wallet.locked_until = None
            wallet.last_error = 'RESET_TO_FLOOR'

    def unlock_after_review(self, agent: str, now: Optional[datetime] = None):
        now = now or self.clock
        wallet = self.wallets[agent]
        if wallet.locked_until and now >= datetime.fromisoformat(wallet.locked_until):
            wallet.balance = INITIAL_BALANCE
            wallet.locked_until = None
            wallet.last_error = None
            wallet.experience += 2.0
            return True
        return False

    def snapshot(self):
        return {'clock_utc': self.clock.isoformat(), 'tick_count': self.tick_count,
                'wallets': self.agent_report(), 'lines': list(self.lines[-200:]),
                'market': self.market}

    def agent_report(self):
        return {k: {'name': w.name, 'balance': round(w.balance, 8),
                     'initial_balance': INITIAL_BALANCE, 'peak_balance': round(w.peak_balance, 8),
                     'trades': w.trades, 'wins': w.wins, 'losses': w.losses,
                     'win_rate': round(w.win_rate, 6), 'experience': round(w.experience, 6),
                     'locked_until': w.locked_until, 'last_error': w.last_error,
                     'open_positions': len(w.positions)} for k, w in self.wallets.items()}
