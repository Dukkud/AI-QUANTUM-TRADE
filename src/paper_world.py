from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
import math

INITIAL_BALANCE = 1000.0
LOCK_DAYS = 5
PROFIT_COMPOUND_FACTOR = 1.0

AGENTS = {
    'Q1': 'Market State', 'Q2': 'Structure & Liquidity', 'Q3': 'Order Flow',
    'Q4': 'Quant Mathematics', 'Q5': 'Geometry & Cycles', 'Q6': 'Macro/News/Geopolitics',
    'Q7': 'ML/Pattern Engine', 'Q8': 'Risk'
}

@dataclass
class Position:
    agent: str; asset: str; direction: str; entry: float; stop: float; target: float
    opened_at: str; qty: float; status: str = 'OPEN'; exit: Optional[float] = None
    pnl: float = 0.0; exit_reason: Optional[str] = None
    mae: float = 0.0; mfe: float = 0.0

@dataclass
class AgentWallet:
    agent: str; name: str; balance: float = INITIAL_BALANCE
    peak_balance: float = INITIAL_BALANCE; wins: int = 0; losses: int = 0
    trades: int = 0; experience: float = 0.0; locked_until: Optional[str] = None
    last_error: Optional[str] = None; positions: List[Position] = field(default_factory=list)
    history: List[dict] = field(default_factory=list); loss_debt: float = 0.0
    @property
    def available(self): return self.balance
    @property
    def win_rate(self): return self.wins / self.trades if self.trades else 0.0
    def is_locked(self, now):
        return bool(self.locked_until and now < datetime.fromisoformat(self.locked_until))

class PaperWorld:
    """24/7-ready deterministic paper world. No real broker/order API is called."""
    def __init__(self):
        self.wallets = {k: AgentWallet(k, v) for k, v in AGENTS.items()}
        self.lines=[]; self.market={}; self.clock=datetime.now(timezone.utc); self.tick_count=0

    def _signal(self, agent, asset, price, tick):
        prev=tick.get('prev', price); move=price-prev
        bias=(sum(ord(c) for c in agent+asset)%3)-1
        direction='LONG' if move*bias>=0 else 'SHORT'
        if abs(move)<1e-12: direction='LONG' if bias>=0 else 'SHORT'
        distance=max(abs(price)*0.002,0.01)
        stop=price-distance if direction=='LONG' else price+distance
        target=price+distance*2 if direction=='LONG' else price-distance*2
        return direction,stop,target

    def _open(self,wallet,asset,price,tick):
        if wallet.is_locked(self.clock) or wallet.positions or wallet.balance < INITIAL_BALANCE: return None
        direction,stop,target=self._signal(wallet.agent,asset,price,tick)
        risk_cash=wallet.balance*0.01; risk_per_unit=abs(price-stop)
        qty=risk_cash/risk_per_unit if risk_per_unit else 0.0
        pos=Position(wallet.agent,asset,direction,price,stop,target,self.clock.isoformat(),qty)
        wallet.positions.append(pos)
        self.lines.append({'agent':wallet.agent,'asset':asset,'direction':direction,'entry':price,
                           'stop_loss':stop,'target':target,'status':'OPEN','opened_at':pos.opened_at})
        return pos

    @staticmethod
    def _update_excursion(pos, price):
        excursion=(price-pos.entry)*pos.qty*(1 if pos.direction=='LONG' else -1)
        pos.mae=min(pos.mae, excursion)
        pos.mfe=max(pos.mfe, excursion)

    def _close(self,wallet,pos,price,reason):
        if pos.status!='OPEN': return
        self._update_excursion(pos, price)
        raw=(price-pos.entry)*pos.qty*(1 if pos.direction=='LONG' else -1)
        pos.exit,pos.status,pos.pnl,pos.exit_reason=price,'CLOSED',raw,reason
        wallet.trades+=1
        if raw>0:
            wallet.wins+=1
            profit_rate=raw/max(wallet.balance,INITIAL_BALANCE)
            wallet.balance=max(INITIAL_BALANCE, wallet.balance*(1+PROFIT_COMPOUND_FACTOR*profit_rate))
            wallet.experience += 1.0+math.log1p(raw/INITIAL_BALANCE)
        else:
            wallet.losses+=1; wallet.last_error=reason
            wallet.loss_debt += abs(raw); wallet.balance=max(INITIAL_BALANCE, wallet.balance+raw)
            wallet.experience += 0.5
            if wallet.loss_debt >= INITIAL_BALANCE:
                wallet.locked_until=(self.clock+timedelta(days=LOCK_DAYS)).isoformat()
        wallet.peak_balance=max(wallet.peak_balance,wallet.balance)
        wallet.history.append({'asset':pos.asset,'direction':pos.direction,'entry':pos.entry,'exit':price,
                               'pnl':raw,'reason':reason,'time':self.clock.isoformat(),
                               'balance_after':wallet.balance,'loss_debt':wallet.loss_debt,
                               'mae':pos.mae,'mfe':pos.mfe})

    def tick(self,asset,price,timestamp=None,prev=None):
        self.clock=datetime.fromisoformat(timestamp) if timestamp else datetime.now(timezone.utc)
        tick={'prev':prev if prev is not None else price}; self.market[asset]={'price':price,'time':self.clock.isoformat()}; self.tick_count+=1
        for wallet in self.wallets.values():
            for pos in list(wallet.positions):
                if pos.asset!=asset or pos.status!='OPEN': continue
                self._update_excursion(pos, price)
                hit_sl=price<=pos.stop if pos.direction=='LONG' else price>=pos.stop
                hit_tp=price>=pos.target if pos.direction=='LONG' else price<=pos.target
                if hit_sl: self._close(wallet,pos,pos.stop,'STOP_LOSS')
                elif hit_tp: self._close(wallet,pos,pos.target,'TAKE_PROFIT')
            wallet.positions=[p for p in wallet.positions if p.status=='OPEN']
            if not wallet.positions and not wallet.is_locked(self.clock): self._open(wallet,asset,price,tick)
        return self.snapshot()

    def unlock_after_review(self,agent,now=None):
        now=now or self.clock; wallet=self.wallets[agent]
        if wallet.locked_until and now>=datetime.fromisoformat(wallet.locked_until):
            wallet.balance=INITIAL_BALANCE; wallet.loss_debt=0.0; wallet.locked_until=None
            wallet.last_error=None; wallet.experience+=2.0; return True
        return False

    def snapshot(self):
        return {'clock_utc':self.clock.isoformat(),'tick_count':self.tick_count,'wallets':self.agent_report(),
                'lines':self.lines[-200:],'market':self.market}

    def agent_report(self):
        return {k:{'name':w.name,'balance':round(w.balance,8),'initial_balance':INITIAL_BALANCE,
                    'wallet_floor':INITIAL_BALANCE,'peak_balance':round(w.peak_balance,8),'trades':w.trades,
                    'wins':w.wins,'losses':w.losses,'win_rate':round(w.win_rate,6),'experience':round(w.experience,6),
                    'locked_until':w.locked_until,'last_error':w.last_error,'loss_debt':round(w.loss_debt,8),
                    'open_positions':len(w.positions)} for k,w in self.wallets.items()}
