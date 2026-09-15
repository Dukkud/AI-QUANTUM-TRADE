from src.hourly_telemetry import HourlyTelemetryLedger, build_hourly_record


def test_hourly_record_contains_required_fields(tmp_path):
    r=build_hourly_record(hour_id='2026-09-16T00:00:00+00:00',trades=[{'pnl':2,'mae':-0.4,'mfe':3.0},{'pnl':-1,'mae':-1.2,'mfe':0.5}],weights={'Q1':.5},regime='TREND_UP',learning={'Q1':{'experience':2}},loss_debt=1.0,quarantine={'Q2':'x'},errors=['E1'],gate={'status':'HOLD'},brier=.12,drawdown=2.5)
    assert r.trades==2 and r.pnl==1 and r.win_rate==.5
    assert r.profit_factor==2.0 and r.ev==.5
    assert r.mae==-0.8 and r.mfe==1.75
    assert r.weights=={'Q1':.5} and r.regime=='TREND_UP'
    assert r.learning and r.loss_debt==1.0 and r.quarantine and r.errors==['E1'] and r.gate['status']=='HOLD'


def test_persistent_round_trip_and_hour_comparison(tmp_path):
    path=tmp_path/'telemetry.jsonl'; ledger=HourlyTelemetryLedger(str(path))
    a=build_hourly_record(hour_id='H0',trades=[{'pnl':1}],weights={'Q1':.5},brier=.1)
    b=build_hourly_record(hour_id='H1',trades=[{'pnl':3},{'pnl':-1}],weights={'Q1':.7},brier=.2)
    ledger.append(a); ledger.append(b)
    assert ledger.latest().hour_id=='H1' and ledger.previous().hour_id=='H0'
    c=ledger.compare(b,a)
    assert c['available'] is True
    assert c['delta']['trades']==1
    assert c['delta']['pnl']==1.0
    assert c['delta']['brier']==.1
    assert c['weights_changed'] is True


def test_first_hour_is_explicitly_without_comparison(tmp_path):
    ledger=HourlyTelemetryLedger(str(tmp_path/'t.jsonl'))
    a=build_hourly_record(hour_id='H0',trades=[])
    ledger.append(a)
    assert ledger.compare(a,None)=={'available':False,'reason':'NO_PREVIOUS_HOUR'}
