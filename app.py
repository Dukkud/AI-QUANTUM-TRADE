from fastapi import FastAPI
from datetime import datetime, timezone
from src.ai_quantum_core import QuantumCore, TradeCandidate
from src.risk_engine import RiskEngine
from src.adaptive_engine import AdaptiveEngine

app=FastAPI(title='AI-QUANTUM-TRADE',version='30.0.0')
core=QuantumCore(); risk=RiskEngine(); adaptive=AdaptiveEngine()

@app.get('/health')
def health():
    return {'status':'ok','mode':'paper','live_trading':False,'emergency_stop':True,'version':'30.0.0'}

@app.get('/state')
def state():
    return {'utc':datetime.now(timezone.utc).isoformat(),'assets':['XAUUSD','BTCUSDT'],'timeframes':['1M','5M','15M','30M','1H','2H','4H','1D','1W'],'agent_weights':adaptive.weights()}

@app.post('/decision')
def decision(payload: dict):
    c=TradeCandidate(**payload)
    d=core.decide(c)
    return {'decision':d,'rr':c.rr,'ev_r':c.ev_r,'risk_pct':risk.position_risk_pct(c.probability, d=='APPROVE_REDUCED_SIZE')}
