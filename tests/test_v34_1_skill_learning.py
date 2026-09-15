from src.skill_evidence import SkillEvidenceLedger

def test_skill_learning_persists_and_settles(tmp_path):
    ledger=SkillEvidenceLedger(str(tmp_path/'skills.jsonl'))
    ledger.record(skill_name='web-research',agent='Q6',asset='XAUUSD',timeframe='1H',regime='TREND_UP',timestamp='2026-09-16T01:00:00+00:00',invoked=True,evidence_count=3,contribution=0.5)
    assert ledger.settle(skill_name='web-research',agent='Q6',asset='XAUUSD',timeframe='1H',timestamp='2026-09-16T01:00:00+00:00',outcome_r=1.2)==1
    matrix=ledger.matrix()
    assert matrix['groups'][0]['settled']==1
    assert matrix['groups'][0]['mean_outcome_r']==1.2

def test_skill_learning_is_research_only(tmp_path):
    ledger=SkillEvidenceLedger(str(tmp_path/'skills.jsonl'))
    snap=ledger.snapshot()
    assert snap['research_only'] is True
    assert snap['live_execution'] is False
