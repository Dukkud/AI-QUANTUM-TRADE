import pytest
from src.regime_replay import ReplayCase,replay

def test_all_project_regimes_replay():
    regimes=("TREND","RANGE","HIGH_VOLATILITY","LOW_VOLATILITY","NEWS_SHOCK","LIQUIDITY_STRESS")
    r=replay(tuple(ReplayCase("XAUUSD","1H",x,1.0) for x in regimes)); assert set(r)==set(regimes)
def test_unknown_regime_rejected():
    with pytest.raises(ValueError): replay((ReplayCase("BTCUSDT","5M","ALIEN",1),))
