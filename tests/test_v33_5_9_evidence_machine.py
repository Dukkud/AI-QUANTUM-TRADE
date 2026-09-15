import json
from src.agent_evidence_attribution import AgentEvidenceAttribution
from src.evidence_machine import EvidenceMachine
from src.evidence_persistence import JsonlEvidenceStore
from src.paper_world import PaperWorld

def council(): return {'agents':[{'agent':f'Q{i}','decision':'LONG','confidence':0.5,'evidence_count':2,'veto':False} for i in range(1,9)]}

def test_persistent_store_chain_and_tamper_detection(tmp_path):
    p=tmp_path/'evidence.jsonl'; s=JsonlEvidenceStore(p); s.append({'type':'x','n':1}); s.append({'type':'x','n':2}); assert s.verify()['valid'] is True
    rows=p.read_text(encoding='utf-8').splitlines(); row=json.loads(rows[0]); row['n']=99; rows[0]=json.dumps(row,sort_keys=True,separators=(',',':')); p.write_text('\n'.join(rows)+'\n',encoding='utf-8'); assert s.verify()['valid'] is False

def test_attribution_survives_restart(tmp_path):
    path=str(tmp_path/'attr.jsonl'); a=AgentEvidenceAttribution(path); a.record_council(asset='XAUUSD',timeframe='M15',timestamp='2026-09-16T00:00:00+00:00',council=council()); assert a.settle(asset='XAUUSD',observation_timestamp='2026-09-16T00:00:00+00:00',outcome_r=1.0,mae_r=-0.2,mfe_r=1.4)==8
    b=AgentEvidenceAttribution(path); assert b.summary('Q1')['settled']==1 and b.summary('Q1')['accuracy']==1.0 and b.integrity()['valid'] is True

def test_evidence_machine_exposes_analytics_and_brier(tmp_path,monkeypatch):
    monkeypatch.setenv('AI_QUANTUM_ATTRIBUTION_PATH',str(tmp_path/'a.jsonl')); monkeypatch.setenv('AI_QUANTUM_PREDICTION_PATH',str(tmp_path/'p.jsonl')); e=EvidenceMachine(); e.observe(asset='BTCUSDT',price=100.0,timestamp='2026-09-16T00:00:00+00:00',payload={'timeframe':'1H','model_version':'m1','ml_probability':0.9,'ml_calibrated':True}); e.observe(asset='BTCUSDT',price=101.0,timestamp='2026-09-16T00:01:00+00:00',payload={'timeframe':'1H'}); assert abs(e.brier()-0.01)<1e-12; assert len(e.attribution_records())==16; assert e.integrity()['attribution']['valid'] and e.integrity()['predictions']['valid']

def test_paper_trade_settlement_contains_r_mae_mfe():
    p=PaperWorld(); p.tick('XAUUSD',2000.0,'2026-09-16T00:00:00+00:00'); p.tick('XAUUSD',2004.0,'2026-09-16T00:01:00+00:00'); p.tick('XAUUSD',1995.0,'2026-09-16T00:02:00+00:00'); row=p.wallets['Q1'].history[0]; assert all(k in row for k in ('opened_at','outcome_r','mae_r','mfe_r'))

def test_learning_remains_non_blocking_and_live_closed():
    e=EvidenceMachine(); c=e.observe(asset='XAUUSD',price=2000.0,timestamp='2026-09-16T00:00:00+00:00'); assert e.snapshot()['research_only'] is True and e.snapshot()['live_execution'] is False; assert 'quantum_decision' in c
