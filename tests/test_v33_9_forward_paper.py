from src.forward_paper import ForwardObservation, ForwardPaperValidator


def test_forward_paper_accumulates_and_stays_research_only():
    v=ForwardPaperValidator()
    for i in range(30):
        v.observe(ForwardObservation(timestamp=f'2026-09-16T00:{i:02d}:00+00:00',asset='XAUUSD',timeframe='M15',decision='LONG',outcome_r=1.0 if i%2==0 else -0.5,cost_r=0.05,regime='TREND_UP'))
    m=v.metrics(min_trades=30)
    assert m['ready_for_statistical_review'] is True
    assert m['settled_trades']==30
    assert m['research_only'] is True and m['live_execution'] is False
    assert m['profit_factor'] > 1
