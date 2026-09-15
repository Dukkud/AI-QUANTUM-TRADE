from fastapi import FastAPI
from datetime import datetime, timezone
from src.ai_quantum_core import QuantumCore, TradeCandidate
from src.risk_engine import RiskEngine
from src.adaptive_engine import AdaptiveEngine
from src.paper_world import PaperWorld
from src.live_gate import ClientLiveGate

app=FastAPI(title='AI-QUANTUM-TRADE',version='31.0.0')
core=QuantumCore(); risk=RiskEngine(); adaptive=AdaptiveEngine()
paper=PaperWorld(); live_gate=ClientLiveGate()

@app.get('/health')
def health():
    return {'status':'ok','mode':'paper','live_trading':False,'emergency_stop':True,'version':'31.0.0'}

@app.get('/state')
def state():
    return {'utc':datetime.now(timezone.utc).isoformat(),'assets':['XAUUSD','BTCUSDT'],'timeframes':['1M','5M','15M','30M','1H','2H','4H','1D','1W'],'agent_weights':adaptive.weights(),'paper_world':paper.snapshot()}

@app.post('/decision')
def decision(payload: dict):
    c=TradeCandidate(**payload)
    d=core.decide(c)
    return {'decision':d,'rr':c.rr,'ev_r':c.ev_r,'risk_pct':risk.position_risk_pct(c.probability, d=='APPROVE_REDUCED_SIZE')}

@app.get('/paper/world')
def paper_world():
    return paper.snapshot()

@app.post('/paper/tick')
def paper_tick(payload: dict):
    return paper.tick(payload['asset'], float(payload['price']), payload.get('timestamp'), payload.get('prev'))

@app.get('/paper/agents')
def paper_agents():
    return paper.agent_report()

@app.get('/paper/trades')
def paper_trades():
    return {k:w.history for k,w in paper.wallets.items()}

@app.get('/paper/lines')
def paper_lines():
    return paper.lines[-500:]

@app.get('/paper/report')
def paper_report():
    return {'generated_at':datetime.now(timezone.utc).isoformat(),'agents':paper.agent_report(),'market':paper.market,'tick_count':paper.tick_count}

@app.post('/account/register')
def register_account(payload: dict):
    a=live_gate.register(payload['account_id'], payload['provider'])
    return {'account_id':a.account_id,'provider':a.provider,'verified':a.verified,'trading_confirmed':a.trading_confirmed}

@app.post('/account/{account_id}/verify')
def verify_account(account_id: str):
    live_gate.verify(account_id)
    return {'account_id':account_id,'verified':True}

@app.post('/account/{account_id}/confirm-trading')
def confirm_trading(account_id: str):
    live_gate.confirm_trading(account_id)
    return {'account_id':account_id,'trading_confirmed':True}

@app.post('/live/gate')
def live_gate_status(payload: dict):
    account_id=payload['account_id']
    safety=payload.get('safety_gates',{})
    return {'can_trade_live':live_gate.can_trade_live(account_id,safety,payload.get('live_trading',False),payload.get('emergency_stop',True))}
