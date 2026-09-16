from src.ai_quantum_core import QuantumCore, TradeCandidate
from src.risk_engine import RiskEngine


def candidate(**kw):
    base=dict(asset='XAUUSD',timeframe='15M',direction='LONG',entry=100,stop=95,target=115,probability=.70,avg_win_r=3,avg_loss_r=1,data_quality=1,news_risk=.1,agent_agreement=.8)
    base.update(kw)
    return TradeCandidate(**base)


def test_positive_ev_approved(): assert QuantumCore().decide(candidate())=='APPROVE'
def test_bad_data_blocks(): assert QuantumCore().decide(candidate(data_quality=.9))=='NO_TRADE'
def test_negative_ev_blocks(): assert QuantumCore().decide(candidate(probability=.2))=='NO_TRADE'
def test_xau_stale_external_data_blocks(): assert QuantumCore().decide(candidate(external_data_fresh=False))=='NO_TRADE'
def test_non_xau_external_freshness_does_not_change_core():
    assert QuantumCore().decide(candidate(asset='BTCUSDT', external_data_fresh=False))=='APPROVE'
def test_live_gate_fail_closed(): assert RiskEngine().live_ready({}) is False
