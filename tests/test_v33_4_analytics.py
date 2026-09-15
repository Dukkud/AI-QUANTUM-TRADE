from src.evidence_analytics import EvidenceAnalytics


def test_grouping_by_regime_asset_timeframe_and_agent():
    rows = [
        {"agent":"Q1","asset":"XAUUSD","timeframe":"M15","regime":"TREND_UP","correct":True,"outcome_r":1.0,"mae_r":-0.2,"mfe_r":1.3,"contribution":0.5},
        {"agent":"Q1","asset":"BTCUSDT","timeframe":"1H","regime":"RANGE","correct":False,"outcome_r":-1.0,"mae_r":-0.8,"mfe_r":0.2,"contribution":0.4},
    ]
    a = EvidenceAnalytics(rows).matrix()
    assert a["by_agent"]["Q1"]["settled"] == 2
    assert a["by_asset"]["XAUUSD"]["accuracy"] == 1.0
    assert a["by_timeframe"]["1H"]["mean_outcome_r"] == -1.0
    assert a["by_regime"]["TREND_UP"]["mean_mfe_r"] == 1.3
    assert a["research_only"] is True
    assert a["live_execution"] is False
