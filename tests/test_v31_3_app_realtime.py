from app import health, realtime_policy_endpoint, realtime_status, realtime_tick
from src.realtime_training import ASSETS, AGENTS, TIMEFRAMES


def test_health_is_paper_only():
    body = health()
    assert body['version'] == '32.0.0'
    assert body['mode'] == 'paper'
    assert body['live_trading'] is False
    assert body['emergency_stop'] is True
    assert body['github_integrations'] == 'enabled_research_only'
    assert body['edge_validation'] == 'research_only'


def test_realtime_policy_exposes_all_assets_timeframes_and_agents():
    body = realtime_policy_endpoint()
    assert body['assets'] == list(ASSETS)
    assert body['timeframes'] == list(TIMEFRAMES)
    assert body['agents'] == list(AGENTS)
    assert body['execution'] == 'PAPER_ONLY'
    assert body['live_orders'] is False


def test_realtime_tick_enters_paper_world_without_live_execution():
    body = realtime_tick({
        'venue': 'binance',
        'symbol': 'BTCUSDT',
        'last': 100000.0,
        'volume': 1.25,
        'exchange_ts_ms': 1000000,
        'received_ts_ms': 1000010,
        'stream': 'aggTrade',
        'timestamp': '2026-01-01T00:00:00+00:00',
        'prev': 99990.0,
    })
    assert body['tick']['venue'] == 'binance'
    assert body['tick']['symbol'] == 'BTCUSDT'
    assert body['tick']['feed_latency_ms'] == 10
    assert body['tick']['training_only'] is True
    assert body['paper']['market']['BTCUSDT']['price'] == 100000.0
    assert body['live_execution'] is False


def test_realtime_status_never_advertises_external_connection_as_verified():
    body = realtime_status()
    assert body['external_connection_verified'] is False
    assert body['execution'] == 'PAPER_ONLY'
    assert body['live_orders'] is False
