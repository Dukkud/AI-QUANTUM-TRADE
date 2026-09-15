from src.realtime_market import MarketTick
from src.training_latency import LatencyObservation, TrainingJournal


def test_market_tick_latency_is_explicit():
    tick = MarketTick('binance', 'BTCUSDT', None, None, 100000.0, 1.0, 1000, 1007, 'aggTrade')
    assert tick.training_only is True
    assert tick.feed_latency_ms == 7
    assert tick.to_dict()['feed_latency_ms'] == 7


def test_training_journal_marks_live_latency_as_not_guaranteed():
    j = TrainingJournal()
    j.record(LatencyObservation(7, 3, 25, 0.5, 'binance'))
    s = j.summary()
    assert s['count'] == 1
    assert s['avg_feed_latency_ms'] == 7
    assert s['live_latency_not_guaranteed'] is True


def test_no_live_execution_surface_in_market_adapter():
    from src.realtime_market import MT5MarketData
    assert not hasattr(MT5MarketData, 'order_send')
