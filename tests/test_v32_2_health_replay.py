from app import APP_VERSION, health, market_replay_endpoint

def test_v32_2_health_and_replay_boundary():
    body=health(); assert body['version']==APP_VERSION; assert body['market_replay']=='deterministic_research_only'
    result=market_replay_endpoint({'bars':[
        {'timestamp_ms':0,'asset':'XAUUSD','timeframe':'1M','open':2500,'high':2502,'low':2499,'close':2501},
        {'timestamp_ms':60000,'asset':'XAUUSD','timeframe':'1M','open':2501,'high':2503,'low':2500,'close':2502},
    ]})
    assert result['validation']['valid'] is True; assert result['research_only'] is True; assert result['live_execution'] is False; assert len(result['events'])==2
