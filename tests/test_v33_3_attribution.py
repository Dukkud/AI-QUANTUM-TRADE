from src.agent_evidence_attribution import AgentEvidenceAttribution


def test_all_agents_are_attributed_and_missing_agents_are_explicit():
    ledger = AgentEvidenceAttribution()
    rows = ledger.record_council(
        asset="XAUUSD", timeframe="M15", timestamp="2026-09-15T20:00:00Z",
        council={"agents": [
            {"agent": "Q1", "decision": "LONG", "confidence": 0.8, "evidence_count": 4},
            {"agent": "Q2", "decision": "SHORT", "confidence": 0.2, "evidence_count": 2},
        ]}, outcome_r=1.0, mae_r=-0.2, mfe_r=1.4,
    )
    assert len(rows) == 8
    assert {r["agent"] for r in rows} == {f"Q{i}" for i in range(1, 9)}
    assert rows[0]["correct"] is True
    assert rows[1]["correct"] is False
    assert rows[2]["decision"] == "DATA_UNAVAILABLE"


def test_summary_is_deterministic_and_research_only():
    ledger = AgentEvidenceAttribution()
    ledger.record_council(
        asset="BTCUSDT", timeframe="1H", timestamp="2026-09-15T21:00:00Z",
        council={"agents": [{"agent": "Q1", "decision": "LONG", "confidence": 1.0, "evidence_count": 3}]},
        outcome_r=-1.0,
    )
    summary = ledger.summary("Q1")
    assert summary["research_only"] is True
    assert summary["live_execution"] is False
    assert summary["settled"] == 1
    assert summary["accuracy"] == 0.0
