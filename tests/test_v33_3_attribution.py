from src.agent_evidence_attribution import AgentEvidenceAttribution

def test_all_agents_are_attributed_and_missing_agents_are_explicit(tmp_path):
    ledger=AgentEvidenceAttribution(str(tmp_path/'a.jsonl')); rows=ledger.record_council(asset='XAUUSD',timeframe='M15',timestamp='2026-09-15T20:00:00Z',council={'agents':[{'agent':'Q1','decision':'BIAS_UP','confidence':0.8,'evidence_count':4},{'agent':'Q2','decision':'BIAS_DOWN','confidence':0.2,'evidence_count':2}]})
    assert len(rows)==8; assert {r['agent'] for r in rows}=={f'Q{i}' for i in range(1,9)}; assert rows[0]['correct'] is None; assert rows[2]['decision']=='DATA_UNAVAILABLE'; assert rows[0]['contribution']>rows[1]['contribution']

def test_settlement_updates_all_agent_records_for_one_council(tmp_path):
    ledger=AgentEvidenceAttribution(str(tmp_path/'a.jsonl')); ledger.record_council(asset='XAUUSD',timeframe='M15',timestamp='2026-09-15T20:00:00Z',council={'agents':[{'agent':'Q1','decision':'BIAS_UP','confidence':1.0,'evidence_count':3},{'agent':'Q2','decision':'BIAS_DOWN','confidence':1.0,'evidence_count':3}]})
    assert ledger.settle(asset='XAUUSD',observation_timestamp='2026-09-15T20:00:00Z',outcome_r=1.0,mae_r=-0.2,mfe_r=1.4)==8; assert ledger.summary('Q1')['accuracy']==1.0; assert ledger.summary('Q2')['accuracy']==0.0

def test_summary_is_research_only(tmp_path):
    ledger=AgentEvidenceAttribution(str(tmp_path/'a.jsonl')); summary=ledger.summary('Q1'); assert summary['research_only'] is True; assert summary['live_execution'] is False
