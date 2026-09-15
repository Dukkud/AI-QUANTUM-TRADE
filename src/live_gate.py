from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List

@dataclass
class Account:
    account_id: str
    provider: str
    verified: bool = False
    trading_confirmed: bool = False
    audit: List[dict] = field(default_factory=list)

class ClientLiveGate:
    """Fail-closed authorization boundary. It does not place orders."""
    def __init__(self):
        self.accounts: Dict[str, Account] = {}

    def register(self, account_id: str, provider: str) -> Account:
        account = Account(account_id=account_id, provider=provider)
        account.audit.append({'event':'REGISTERED','time':datetime.now(timezone.utc).isoformat()})
        self.accounts[account_id] = account
        return account

    def verify(self, account_id: str):
        account = self.accounts[account_id]
        account.verified = True
        account.audit.append({'event':'ACCOUNT_VERIFIED','time':datetime.now(timezone.utc).isoformat()})

    def confirm_trading(self, account_id: str):
        account = self.accounts[account_id]
        if not account.verified:
            raise ValueError('ACCOUNT_NOT_VERIFIED')
        account.trading_confirmed = True
        account.audit.append({'event':'CLIENT_CONFIRMED_TRADING','time':datetime.now(timezone.utc).isoformat()})

    def can_trade_live(self, account_id: str, safety_gates: dict, live_trading: bool=False, emergency_stop: bool=True):
        account = self.accounts.get(account_id)
        required = ['real_data_verified','data_quality_pass','reconciliation_pass','paper_execution_pass','risk_engine_pass']
        safety_ok = all(bool(safety_gates.get(k)) for k in required)
        return bool(account and account.verified and account.trading_confirmed and safety_ok and live_trading and not emergency_stop)
